from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Shelter, Donation
from users.models import User
from animals.models import Animal


class ShelterListTest(TestCase):
    """收容所列表测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.shelter1 = Shelter.objects.create(
            name='北京爱心基地',
            address='北京市朝阳区',
            contact_name='张三',
            contact_phone='13800138000',
            email='beijing@shelter.com',
            capacity=100,
            description='专业的动物救助基地'
        )
        self.shelter2 = Shelter.objects.create(
            name='上海流浪动物之家',
            address='上海市浦东新区',
            contact_name='李四',
            contact_phone='13800138001',
            email='shanghai@shelter.com',
            capacity=150,
            description='致力于流浪动物救助'
        )
        
    def test_get_shelters_list(self):
        """测试获取收容所列表"""
        url = reverse('shelter-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)
        
    def test_search_shelter_by_name(self):
        """测试按名称搜索收容所"""
        url = reverse('shelter-list') + '?search=北京'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], '北京爱心基地')


class ShelterDetailTest(TestCase):
    """收容所详情测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.shelter = Shelter.objects.create(
            name='北京爱心基地',
            address='北京市朝阳区',
            contact_name='王五',
            contact_phone='13800138002',
            email='beijing2@shelter.com',
            capacity=200,
            description='专业的动物救助基地'
        )
        
    def test_get_shelter_detail(self):
        """测试获取收容所详情"""
        url = reverse('shelter-detail', kwargs={'pk': self.shelter.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], '北京爱心基地')


class DonationTest(TestCase):
    """捐赠测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='donor',
            password='testpass123'
        )
        self.shelter = Shelter.objects.create(
            name='北京爱心基地',
            address='北京市朝阳区',
            contact_name='赵六',
            contact_phone='13800138003',
            email='beijing3@shelter.com',
            capacity=250
        )
        self.client.force_authenticate(user=self.user)
        
    def test_create_donation(self):
        """测试创建捐赠"""
        url = reverse('donation-list')
        data = {
            'shelter': self.shelter.id,
            'amount': 100.00,
            'donation_type': 'money',
            'remarks': '支持动物救助事业'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Donation.objects.filter(
            donor=self.user,
            shelter=self.shelter
        ).exists())
        
    def test_get_user_donations(self):
        """测试获取用户捐赠记录"""
        Donation.objects.create(
            donor=self.user,
            shelter=self.shelter,
            amount=100.00,
            donation_type='money',
            status='completed'
        )
        url = reverse('donation-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
