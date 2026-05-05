from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Animal
from users.models import User
from shelters.models import Shelter


class AnimalListTest(TestCase):
    """动物列表测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.shelter = Shelter.objects.create(
            name='测试基地',
            address='北京市朝阳区',
            contact_name='张三',
            contact_phone='13800138000',
            email='test@shelter.com',
            capacity=100
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
            name='大黄',
            species='dog',
            breed='金毛',
            age=24,
            gender='male',
            weight=25.0,
            status='available',
            description='忠诚的狗狗',
            personality='活泼好动',
            health_status='健康',
            images=[],
            found_place='北京市海淀区',
            found_date='2024-02-01',
            shelter=self.shelter
        )
        
    def test_get_animals_list(self):
        """测试获取动物列表"""
        url = reverse('animal-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)
        
    def test_filter_animals_by_species(self):
        """测试按物种筛选动物"""
        url = reverse('animal-list') + '?species=cat'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], '小白')
        
    def test_filter_animals_by_status(self):
        """测试按状态筛选动物"""
        url = reverse('animal-list') + '?status=available'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)


class AnimalDetailTest(TestCase):
    """动物详情测试"""
    
    def setUp(self):
        self.client = APIClient()
        self.shelter = Shelter.objects.create(
            name='测试基地',
            address='北京市朝阳区',
            contact_name='李四',
            contact_phone='13800138001',
            email='test2@shelter.com',
            capacity=150
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
        
    def test_get_animal_detail(self):
        """测试获取动物详情"""
        url = reverse('animal-detail', kwargs={'pk': self.animal.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], '小白')
        
    def test_nonexistent_animal(self):
        """测试不存在的动物"""
        url = reverse('animal-detail', kwargs={'pk': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PersonalityMatchTest(TestCase):
    """性格匹配测试"""
    
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
            contact_phone='13800138002',
            email='test3@shelter.com',
            capacity=200
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
            shelter=self.shelter,
            animal_openness=4.0,
            animal_agreeableness=4.5,
            animal_extraversion=3.5,
            animal_conscientiousness=3.8,
            animal_neuroticism=2.5
        )
        self.client.force_authenticate(user=self.user)
        
    def test_personality_match(self):
        """测试性格匹配计算"""
        url = reverse('animal-personality-match')
        data = {
            'animal_id': self.animal.id,
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
        self.assertIn('animal_traits', response.data['data'])
        
    def test_match_with_missing_scores(self):
        """测试缺少分数的匹配请求"""
        url = reverse('animal-personality-match')
        data = {
            'animal_id': self.animal.id,
            'user_scores': {
                'openness': 4.0
            }
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_match_with_invalid_score(self):
        """测试无效分数的匹配请求"""
        url = reverse('animal-personality-match')
        data = {
            'animal_id': self.animal.id,
            'user_scores': {
                'openness': 6.0,
                'conscientiousness': 3.5,
                'extraversion': 4.2,
                'agreeableness': 4.5,
                'neuroticism': 2.5
            }
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
