from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from community.models import Post, Comment
from users.models import User


class PostTest(TestCase):
    """帖子测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='poster',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_create_post(self):
        """测试创建帖子"""
        url = reverse('post-list')
        data = {
            'title': '我的领养经历',
            'content': '分享我与小白的故事...',
            'category': 'experience'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Post.objects.filter(title='我的领养经历').exists())
        
    def test_get_posts_list(self):
        """测试获取帖子列表"""
        Post.objects.create(
            author=self.user,
            title='测试帖子',
            content='测试内容',
            category='experience'
        )
        url = reverse('post-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)


class CommentTest(TestCase):
    """评论测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='commenter',
            password='testpass123'
        )
        self.author = User.objects.create_user(
            username='author',
            password='testpass123'
        )
        self.post = Post.objects.create(
            author=self.author,
            title='测试帖子',
            content='测试内容',
            category='experience'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_create_comment(self):
        """测试创建评论"""
        url = reverse('comment-list')
        data = {
            'post': self.post.id,
            'content': '很好的分享！'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Comment.objects.filter(
            author=self.user,
            post=self.post
        ).exists())
