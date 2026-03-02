import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

class CommunityConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'community_room'
        
        # 加入房间组
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        # 离开房间组
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'new_post':
            await self.handle_new_post(data)
        elif message_type == 'new_comment':
            await self.handle_new_comment(data)
        elif message_type == 'like_post':
            await self.handle_like_post(data)
        elif message_type == 'join_room':
            await self.handle_join_room(data)

    async def handle_new_post(self, data):
        """处理新帖子"""
        post_data = data.get('post')
        
        # 保存到数据库（异步）
        post = await self.create_post(post_data)
        
        # 广播给所有连接的客户端
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'post_message',
                'message': {
                    'type': 'new_post',
                    'post': {
                        'id': post.id,
                        'title': post.title,
                        'content': post.content,
                        'author': post.author.username,
                        'category': post.category,
                        'likes': post.likes,
                        'created_at': post.created_at.isoformat(),
                    }
                }
            }
        )

    async def handle_new_comment(self, data):
        """处理新评论"""
        comment_data = data.get('comment')
        
        # 保存评论到数据库
        comment = await self.create_comment(comment_data)
        
        # 广播给所有连接的客户端
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'comment_message',
                'message': {
                    'type': 'new_comment',
                    'comment': {
                        'id': comment.id,
                        'content': comment.content,
                        'author': comment.author.username,
                        'post_id': comment.post.id,
                        'created_at': comment.created_at.isoformat(),
                    }
                }
            }
        )

    async def handle_like_post(self, data):
        """处理点赞"""
        post_id = data.get('post_id')
        user_id = data.get('user_id')
        
        # 更新点赞数
        post = await self.update_post_likes(post_id)
        
        # 广播给所有连接的客户端
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'like_message',
                'message': {
                    'type': 'post_like',
                    'post_id': post_id,
                    'likes': post.likes,
                }
            }
        )

    async def handle_join_room(self, data):
        """处理用户加入房间"""
        user_id = data.get('user_id')
        if user_id:
            user = await self.get_user(user_id)
            if user:
                await self.send(text_data=json.dumps({
                    'type': 'user_joined',
                    'message': f'{user.username} 加入了聊天室',
                    'user': user.username
                }))

    # WebSocket事件处理器
    async def post_message(self, event):
        await self.send(text_data=json.dumps(event['message']))

    async def comment_message(self, event):
        await self.send(text_data=json.dumps(event['message']))

    async def like_message(self, event):
        await self.send(text_data=json.dumps(event['message']))

    # 数据库操作方法（使用database_sync_to_async装饰器）
    @database_sync_to_async
    def create_post(self, post_data):
        User = get_user_model()
        Post = self.get_post_model()
        user = User.objects.get(id=post_data['author_id'])
        post = Post.objects.create(
            title=post_data['title'],
            content=post_data['content'],
            author=user,
            category=post_data['category'],
            images=post_data.get('images', [])
        )
        return post

    @database_sync_to_async
    def create_comment(self, comment_data):
        User = get_user_model()
        Post = self.get_post_model()
        Comment = self.get_comment_model()
        user = User.objects.get(id=comment_data['author_id'])
        post = Post.objects.get(id=comment_data['post_id'])
        comment = Comment.objects.create(
            post=post,
            author=user,
            content=comment_data['content']
        )
        return comment

    @database_sync_to_async
    def update_post_likes(self, post_id):
        Post = self.get_post_model()
        post = Post.objects.get(id=post_id)
        post.likes += 1
        post.save()
        return post

    @database_sync_to_async
    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    
    def get_post_model(self):
        from .models import Post
        return Post
    
    def get_comment_model(self):
        from .models import Comment
        return Comment