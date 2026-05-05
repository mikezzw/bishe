from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import AdoptionApplication, AdoptionMatch
from users.models import User
from animals.models import Animal
from shelters.models import Shelter


class AdoptionApplicationTest(TestCase):
    """领养申请测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='applicant',
            password='testpass123',
            phone='13800138000'
        )
        self.shelter = Shelter.objects.create(
            name='测试基地',
            address='北京市朝阳区',
            contact_name='张三',
            contact_phone='13800138001',
            email='test@shelter.com',
            capacity=100
        )
        self.animal = Animal.objects.create(
            name='小白',
            species='cat',
            breed='英短',
            age=12,
            gender='female',
            weight=3.5,
            status='available',
            description='可爱的小猫',
            personality='温顺友善',
            health_status='健康',
            images=[],
            found_place='北京市朝阳区',
            found_date='2024-01-01',
            shelter=self.shelter
        )
        self.client.force_authenticate(user=self.user)
        
    def test_create_application(self):
        """测试创建领养申请"""
        url = reverse('adoption-application-list')
        data = {
            'animal': self.animal.id,
            'application_reason': '我很喜欢小动物，有养猫经验',
            'personal_info': '我有稳定的工作和住所',
            'contact_phone': '13800138000',
            'contact_address': '北京市朝阳区某某街道'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(AdoptionApplication.objects.filter(
            applicant=self.user,
            animal=self.animal
        ).exists())
        
    def test_create_application_unauthenticated(self):
        """测试未登录用户无法创建申请"""
        self.client.force_authenticate(user=None)
        url = reverse('adoption-application-list')
        data = {
            'animal': self.animal.id,
            'application_reason': '我很喜欢小动物',
            'personal_info': '我有稳定的工作',
            'contact_phone': '13800138000',
            'contact_address': '北京市朝阳区'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_get_user_applications(self):
        """测试获取用户的申请列表"""
        AdoptionApplication.objects.create(
            applicant=self.user,
            animal=self.animal,
            application_reason='测试申请',
            personal_info='测试信息',
            contact_phone='13800138000',
            contact_address='北京市朝阳区'
        )
        url = reverse('adoption-application-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)


class ApplicationReviewTest(TestCase):
    """申请审核测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.applicant = User.objects.create_user(
            username='applicant',
            password='testpass123'
        )
        self.reviewer = User.objects.create_user(
            username='reviewer',
            password='testpass123',
            user_type='shelter'
        )
        self.shelter = Shelter.objects.create(
            name='测试基地',
            address='北京市朝阳区',
            contact_name='李四',
            contact_phone='13800138002',
            email='test2@shelter.com',
            capacity=150,
            manager=self.reviewer
        )
        self.animal = Animal.objects.create(
            name='小白',
            species='cat',
            breed='英短',
            age=12,
            gender='female',
            weight=3.5,
            status='pending',
            description='可爱的小猫',
            personality='温顺友善',
            health_status='健康',
            images=[],
            found_place='北京市朝阳区',
            found_date='2024-01-01',
            shelter=self.shelter
        )
        self.application = AdoptionApplication.objects.create(
            applicant=self.applicant,
            animal=self.animal,
            application_reason='测试申请',
            personal_info='测试信息',
            contact_phone='13800138000',
            contact_address='北京市朝阳区',
            status='pending'
        )
        self.client.force_authenticate(user=self.reviewer)
        
    def test_approve_application(self):
        """测试批准申请"""
        url = reverse('adoption-application-review', kwargs={'pk': self.application.id})
        data = {
            'action': 'approve',
            'comments': '审核通过'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'approved')
        self.assertIsNotNone(self.application.reviewed_at)
        
    def test_reject_application(self):
        """测试拒绝申请"""
        url = reverse('adoption-application-review', kwargs={'pk': self.application.id})
        data = {
            'action': 'reject',
            'comments': '不符合领养条件'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'rejected')


class AdoptionMatchTest(TestCase):
    """领养匹配测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            openness=4.0,
            conscientiousness=3.5,
            extraversion=4.2,
            agreeableness=4.5,
            neuroticism=2.5
        )
        self.shelter = Shelter.objects.create(
            name='测试基地',
            address='北京市朝阳区',
            contact_name='王五',
            contact_phone='13800138003',
            email='test3@shelter.com',
            capacity=200
        )
        self.animal1 = Animal.objects.create(
            name='小白',
            species='cat',
            breed='英短',
            age=12,
            gender='female',
            weight=3.5,
            status='available',
            description='可爱的小猫',
            personality='温顺友善',
            health_status='健康',
            images=[],
            found_place='北京市朝阳区',
            found_date='2024-01-01',
            shelter=self.shelter,
            animal_openness=4.0,
            animal_agreeableness=4.5,
            animal_extraversion=3.5,
            animal_conscientiousness=3.8,
            animal_neuroticism=2.5
        )
        self.animal2 = Animal.objects.create(
            name='小黑',
            species='cat',
            breed='美短',
            age=18,
            gender='male',
            weight=4.0,
            status='available',
            description='活泼的小猫',
            personality='活泼好动',
            health_status='健康',
            images=[],
            found_place='北京市海淀区',
            found_date='2024-02-01',
            shelter=self.shelter,
            animal_openness=3.5,
            animal_agreeableness=4.0,
            animal_extraversion=4.5,
            animal_conscientiousness=3.5,
            animal_neuroticism=3.0
        )
        self.client.force_authenticate(user=self.user)
        
    def test_calculate_match_single_animal(self):
        """测试计算单个动物的匹配度"""
        url = reverse('adoption-calculate-match')
        data = {
            'animal_id': self.animal1.id,
            'user_scores': {
                'openness': 4.0,
                'conscientiousness': 3.5,
                'extraversion': 4.2,
                'agreeableness': 4.5,
                'neuroticism': 2.5
            }
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('match_percentage', response.data['data'])
        
    def test_calculate_match_all_animals(self):
        """测试计算所有可用动物的匹配度"""
        url = reverse('adoption-calculate-match')
        data = {
            'user_scores': {
                'openness': 4.0,
                'conscientiousness': 3.5,
                'extraversion': 4.2,
                'agreeableness': 4.5,
                'neuroticism': 2.5
            }
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('matches', response.data['data'])
        self.assertEqual(len(response.data['data']['matches']), 2)
        
    def test_match_algorithm_accuracy(self):
        """测试匹配算法准确性"""
        url = reverse('adoption-calculate-match')
        # 用户与动物1特征完全一致，应该获得高匹配度
        data = {
            'animal_id': self.animal1.id,
            'user_scores': {
                'openness': 4.0,
                'conscientiousness': 3.8,
                'extraversion': 3.5,
                'agreeableness': 4.5,
                'neuroticism': 2.5
            }
        }
        response = self.client.post(url, data, format='json')
        match_percentage = response.data['data']['match_percentage']
        self.assertGreater(match_percentage, 90)
