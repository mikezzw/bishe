import math
import base64

import requests
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from .models import Animal
from .serializers import AnimalSerializer, AnimalCreateSerializer, AnimalUpdateSerializer
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.baidu_ai import baidu_ai_helper
from utils.cache_utils import (
    cache_animal_list, cache_animal_detail, 
    invalidate_related_caches, CACHE_TIMEOUT
)

class AnimalViewSet(viewsets.ModelViewSet):
    queryset = Animal.objects.all()
    serializer_class = AnimalSerializer
    
    def dispatch(self, request, *args, **kwargs):
        # 对于写操作，清除相关缓存
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            response = super().dispatch(request, *args, **kwargs)
            if response.status_code in [200, 201, 204]:
                # 清除动物相关缓存
                # POST请求不需要获取对象，只有PUT/PATCH/DELETE需要
                if request.method != 'POST':
                    invalidate_related_caches(self.get_object() if hasattr(self, 'get_object') else None)
            return response
        return super().dispatch(request, *args, **kwargs)

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'available_animals', 'personality_match', 'breed_identify']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return AnimalCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return AnimalUpdateSerializer
        return AnimalSerializer

    def list(self, request):
        # 获取查询参数
        shelter_id = request.query_params.get('shelter')
        
        # 构建查询集
        queryset = self.get_queryset()
        
        # 如果提供了shelter参数，过滤出该基地的动物
        if shelter_id:
            queryset = queryset.filter(shelter_id=shelter_id)
        
        # 分页处理
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # 构建分页响应数据
            paginated_response = self.get_paginated_response(serializer.data)
            # 构建最终响应格式
            response_data = {
                'code': 200,
                'message': '获取动物列表成功',
                'data': paginated_response.data
            }
            return Response(response_data)
        
        # 非分页处理
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 200,
            'message': '获取动物列表成功',
            'data': serializer.data
        })

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            animal = serializer.save()
            return Response({
                'code': 200,
                'message': '创建成功',
                'data': AnimalSerializer(animal).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'code': 400,
            'message': '创建失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        animal = self.get_object()
        serializer = self.get_serializer(animal, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'code': 200,
                'message': '更新成功',
                'data': AnimalSerializer(animal).data
            })
        return Response({
            'code': 400,
            'message': '更新失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        animal = self.get_object()
        animal.delete()
        return Response({
            'code': 200,
            'message': '删除成功'
        }, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='available')
    @method_decorator(cache_page(CACHE_TIMEOUT['long']))
    def available_animals(self, request):
        animals = Animal.objects.filter(status='available')
        serializer = AnimalSerializer(animals, many=True)
        return Response({
            'code': 200,
            'message': '获取可领养动物成功',
            'data': serializer.data
        })

    @action(detail=False, methods=['post'], url_path='breed-identify')
    def breed_identify(self, request):
        # 支持多种输入方式：文件上传、base64数据、图片URL
        image_file = request.FILES.get('image')
        image_data = request.data.get('image_data')  # base64格式
        image_url = request.data.get('image_url')
        
        # 验证输入
        if not any([image_file, image_data, image_url]):
            return Response({
                'code': 400,
                'message': '请提供图片文件、base64数据或图片URL'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 处理不同类型的图片输入
            if image_file:
                # 文件上传
                image_content = image_file.read()
                result = baidu_ai_helper.identify_animal_breed(image_content)
            elif image_data:
                # base64数据
                result = baidu_ai_helper.identify_animal_breed(image_data)
            elif image_url:
                # URL方式
                result = baidu_ai_helper.identify_from_url(image_url)
            
            # 处理识别结果
            if result['success']:
                # 提取品种信息
                breed_info = {
                    'breed': result['breed'],
                    'confidence': result['confidence'],
                    'species': self._infer_species_from_breed(result['breed']),
                    'baike_info': result.get('baike_info', {})
                }
                
                return Response({
                    'code': 200,
                    'message': '品种识别成功',
                    'data': breed_info
                })
            else:
                return Response({
                    'code': 400,
                    'message': result['error']
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'code': 500,
                'message': '品种识别失败',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _infer_species_from_breed(self, breed_name):
        """根据品种名称推断物种"""
        dog_keywords = ['犬', '狗', '牧羊犬', '梗', '猎犬', '斗牛', '雪纳瑞', '柯基', '柴犬', '金毛', '拉布拉多']
        cat_keywords = ['猫', '波斯', '暹罗', '英短', '美短', '布偶', '缅因']
        
        for keyword in dog_keywords:
            if keyword in breed_name:
                return 'dog'
        
        for keyword in cat_keywords:
            if keyword in breed_name:
                return 'cat'
        
        return 'other'
    # animals/views.py
    @action(detail=False, methods=['post'], url_path='personality-match')
    def personality_match(self, request):
        animal_id = request.data.get('animal_id')
        if not animal_id:
            return Response({
                'code': 400,
                'message': '请提供动物ID'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            animal = Animal.objects.get(id=animal_id)
        except Animal.DoesNotExist:
            return Response({
                'code': 404,
                'message': '动物不存在'
            }, status=status.HTTP_404_NOT_FOUND)
            
        user_scores = request.data.get('user_scores')

        # 计算欧几里得距离
        distance = math.sqrt(
            (animal.animal_openness - user_scores['openness'])**2 +
            (animal.animal_conscientiousness - user_scores['conscientiousness'])**2 +
            (animal.animal_extraversion - user_scores['extraversion'])**2 +
            (animal.animal_agreeableness - user_scores['agreeableness'])**2 +
            (animal.animal_neuroticism - user_scores['neuroticism'])**2
        )

        # 转换为匹配度百分比 (距离越小匹配度越高)
        match_percentage = max(0, 100 - (distance * 20))

        return Response({
            'code': 200,
            'message': '匹配度计算成功',
            'data': {
                'match_percentage': round(match_percentage, 1),
                'animal_traits': {
                    'openness': animal.animal_openness,
                    'conscientiousness': animal.animal_conscientiousness,
                    'extraversion': animal.animal_extraversion,
                    'agreeableness': animal.animal_agreeableness,
                    'neuroticism': animal.animal_neuroticism
                }
            }
        })
