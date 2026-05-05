from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import User


class UserRegistrationTest(TestCase):
    """用户注册测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('user-register')
        
    def test_user_registration_success(self):
        """测试用户注册成功"""
        data = {
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'test@example.com',
            'phone': '13800138000'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        
    def test_user_registration_duplicate_username(self):
        """测试重复用户名注册失败"""
        User.objects.create_user(username='testuser', password='testpass123')
        data = {
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'test2@example.com'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTest(TestCase):
    """用户登录测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('user-login')
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
    def test_login_success(self):
        """测试登录成功"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data['data'])
        
    def test_login_wrong_password(self):
        """测试密码错误"""
        data = {
            'username': 'testuser',
            'password': 'wrongpass'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserProfileTest(TestCase):
    """用户资料测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_get_profile(self):
        """测试获取用户资料"""
        url = reverse('user-profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['username'], 'testuser')
        
    def test_update_profile(self):
        """测试更新用户资料"""
        url = reverse('user-profile')
        data = {
            'phone': '13800138000',
            'address': '北京市朝阳区'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone, '13800138000')


class PersonalityTestUpdateTest(TestCase):
    """性格测试分数更新测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_update_personality_scores(self):
        """测试更新性格分数"""
        url = reverse('user-update-personality')
        data = {
            'openness': 4.5,
            'conscientiousness': 3.8,
            'extraversion': 4.2,
            'agreeableness': 4.0,
            'neuroticism': 2.5
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.openness, 4.5)
        self.assertEqual(self.user.extraversion, 4.2)
        
    def test_invalid_personality_score(self):
        """测试无效的性格分数"""
        url = reverse('user-update-personality')
        data = {
            'openness': 6.0,
            'conscientiousness': 3.8,
            'extraversion': 4.2,
            'agreeableness': 4.0,
            'neuroticism': 2.5
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
