from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Post, Comment, Notification, Report, ContentModeration, UserFeedback
from .serializers import PostSerializer, PostCreateSerializer, PostUpdateSerializer, CommentSerializer, CommentCreateSerializer, NotificationSerializer, NotificationUpdateSerializer, ReportSerializer, ReportCreateSerializer, ReportUpdateSerializer, ContentModerationSerializer, UserFeedbackSerializer, UserFeedbackCreateSerializer, UserFeedbackUpdateSerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return PostCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return PostUpdateSerializer
        return PostSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            post = serializer.save()
            return Response({
                'code': 200,
                'message': '帖子创建成功',
                'data': PostSerializer(post).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'code': 400,
            'message': '帖子创建失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        post = self.get_object()
        if post.author != request.user:
            return Response({
                'code': 403,
                'message': '没有权限修改此帖子'
            }, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'code': 200,
                'message': '帖子更新成功',
                'data': PostSerializer(post).data
            })
        return Response({
            'code': 400,
            'message': '帖子更新失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        post = self.get_object()
        if post.author != request.user:
            return Response({
                'code': 403,
                'message': '没有权限删除此帖子'
            }, status=status.HTTP_403_FORBIDDEN)
        post.delete()
        return Response({
            'code': 200,
            'message': '帖子删除成功'
        }, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='my-posts')
    def my_posts(self, request):
        posts = Post.objects.filter(author=request.user)
        serializer = PostSerializer(posts, many=True)
        return Response({
            'code': 200,
            'message': '获取我的帖子成功',
            'data': serializer.data
        })

    @action(detail=True, methods=['post'], url_path='like')
    def like_post(self, request, pk=None):
        post = self.get_object()
        user = request.user
        
        # 检查用户是否已经点赞
        from django.contrib.contenttypes.models import ContentType
        from django.contrib.contenttypes.fields import GenericForeignKey
        
        # 创建用户点赞记录模型
        LikeRecord, created = type('LikeRecord', (), {
            '__module__': __name__,
            'Meta': type('Meta', (), {
                'db_table': 'like_records',
                'unique_together': ('user', 'content_type', 'object_id')
            }),
            '__str__': lambda self: f'{self.user.username} likes {self.content_object}'
        })
        
        # 简单实现：直接增加点赞数（实际项目中应使用专门的点赞记录表）
        post.likes += 1
        post.save()
        
        # 创建通知
        Notification.objects.create(
            recipient=post.author,
            sender=user,
            type='like',
            content=f'{user.username} 点赞了你的帖子 {post.title}',
            related_id=post.id
        )
        
        return Response({
            'code': 200,
            'message': '点赞成功',
            'data': {'likes': post.likes, 'liked': True}
        })
    
    @action(detail=True, methods=['post'], url_path='unlike')
    def unlike_post(self, request, pk=None):
        post = self.get_object()
        user = request.user
        
        # 减少点赞数（简单实现）
        if post.likes > 0:
            post.likes -= 1
            post.save()
        
        return Response({
            'code': 200,
            'message': '取消点赞成功',
            'data': {'likes': post.likes, 'liked': False}
        })
    
    @action(detail=True, methods=['get'], url_path='check-like')
    def check_like(self, request, pk=None):
        post = self.get_object()
        user = request.user
        
        # 检查用户是否已点赞（这里简化处理）
        # 实际项目中应该查询点赞记录表
        liked = False  # 简化实现
        
        return Response({
            'code': 200,
            'message': '获取点赞状态成功',
            'data': {'liked': liked, 'likes': post.likes}
        })

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            comment = serializer.save()
            # 创建通知
            notification_content = f'{request.user.username} 评论了你的帖子 {comment.post.title}'
            
            # 如果是回复评论，则通知被回复的用户
            if comment.parent:
                Notification.objects.create(
                    recipient=comment.parent.author,
                    sender=request.user,
                    type='comment',
                    content=f'{request.user.username} 回复了你的评论',
                    related_id=comment.post.id
                )
                notification_content = f'{request.user.username} 回复了 {comment.parent.author.username} 的评论'
            else:
                # 通知帖子作者
                Notification.objects.create(
                    recipient=comment.post.author,
                    sender=request.user,
                    type='comment',
                    content=f'{request.user.username} 评论了你的帖子 {comment.post.title}',
                    related_id=comment.post.id
                )
            
            return Response({
                'code': 200,
                'message': '评论创建成功',
                'data': CommentSerializer(comment).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'code': 400,
            'message': '评论创建失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        comment = self.get_object()
        if comment.author != request.user:
            return Response({
                'code': 403,
                'message': '没有权限删除此评论'
            }, status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response({
            'code': 200,
            'message': '评论删除成功'
        }, status=status.HTTP_204_NO_CONTENT)

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset.filter(recipient=self.request.user)
        # 可以添加额外的过滤条件
        return queryset

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return NotificationUpdateSerializer
        return NotificationSerializer

    @action(detail=False, methods=['get'], url_path='unread')
    def unread_notifications(self, request):
        notifications = self.get_queryset().filter(is_read=False)
        serializer = NotificationSerializer(notifications, many=True)
        return Response({
            'code': 200,
            'message': '获取未读通知成功',
            'data': serializer.data
        })

    @action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self, request):
        notifications = self.get_queryset().filter(is_read=False)
        notifications.update(is_read=True)
        return Response({
            'code': 200,
            'message': '所有通知已标记为已读'
        })


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all().order_by('-created_at')
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReportCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ReportUpdateSerializer
        return ReportSerializer
    
    def get_queryset(self):
        user = self.request.user
        # 普通用户只能看到自己提交的举报
        # 管理员可以看到所有举报
        if hasattr(user, 'is_staff') and user.is_staff:
            return self.queryset
        return self.queryset.filter(reporter=user)
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            report = serializer.save()
            return Response({
                'code': 200,
                'message': '举报提交成功，我们会尽快处理',
                'data': ReportSerializer(report).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'code': 400,
            'message': '举报提交失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='my-reports')
    def my_reports(self, request):
        reports = self.get_queryset().filter(reporter=request.user)
        serializer = ReportSerializer(reports, many=True)
        return Response({
            'code': 200,
            'message': '获取我的举报记录成功',
            'data': serializer.data
        })


class ContentModerationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ContentModeration.objects.all().order_by('-created_at')
    serializer_class = ContentModerationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # 只有管理员可以查看审核记录
        user = self.request.user
        if hasattr(user, 'is_staff') and user.is_staff:
            return self.queryset
        return self.queryset.none()  # 返回空查询集
    
    @action(detail=False, methods=['get'], url_path='stats')
    def moderation_stats(self, request):
        # 获取审核统计信息
        from django.db.models import Count
        stats = {
            'total_moderations': self.queryset.count(),
            'actions_breakdown': dict(
                self.queryset.values('action').annotate(count=Count('action')).values_list('action', 'count')
            ),
            'recent_activity': ContentModerationSerializer(
                self.queryset[:10], many=True
            ).data
        }
        return Response({
            'code': 200,
            'message': '获取审核统计成功',
            'data': stats
        })


class UserFeedbackViewSet(viewsets.ModelViewSet):
    queryset = UserFeedback.objects.all()
    serializer_class = UserFeedbackSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserFeedbackCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserFeedbackUpdateSerializer
        return UserFeedbackSerializer
    
    def get_queryset(self):
        user = self.request.user
        # 普通用户只能看到自己的反馈，管理员可以看到所有反馈
        if hasattr(user, 'is_staff') and user.is_staff:
            return self.queryset
        return self.queryset.filter(user=user)
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            feedback = serializer.save()
            return Response({
                'code': 200,
                'message': '反馈提交成功，我们会尽快处理',
                'data': UserFeedbackSerializer(feedback).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'code': 400,
            'message': '反馈提交失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, pk=None):
        feedback = self.get_object()
        # 只有管理员可以更新反馈状态
        if not (hasattr(request.user, 'is_staff') and request.user.is_staff):
            return Response({
                'code': 403,
                'message': '只有管理员可以处理反馈'
            }, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(feedback, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            feedback = serializer.save()
            return Response({
                'code': 200,
                'message': '反馈处理成功',
                'data': UserFeedbackSerializer(feedback).data
            })
        return Response({
            'code': 400,
            'message': '反馈处理失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='my-feedbacks')
    def my_feedbacks(self, request):
        feedbacks = self.get_queryset().filter(user=request.user)
        serializer = UserFeedbackSerializer(feedbacks, many=True)
        return Response({
            'code': 200,
            'message': '获取我的反馈记录成功',
            'data': serializer.data
        })
