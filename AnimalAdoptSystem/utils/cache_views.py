from django.http import JsonResponse
from django.core.cache import cache
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
import json
import logging
from utils.cache_utils import (
    invalidate_cache_pattern, 
    CACHE_PREFIX, 
    CACHE_TIMEOUT
)

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([AllowAny])
def cache_status(request):
    """获取缓存状态信息"""
    try:
        # 测试缓存连接
        cache.set('cache_test', 'working', 30)
        cache_result = cache.get('cache_test')
        
        # 获取各种缓存统计信息
        stats = {
            'cache_backend': 'Redis' if 'redis' in str(type(cache)) else 'Local Memory',
            'connection_status': 'Connected' if cache_result else 'Disconnected',
            'test_key_value': cache_result,
            'cache_prefixes': CACHE_PREFIX,
            'timeout_settings': CACHE_TIMEOUT
        }
        
        return Response({
            'code': 200,
            'message': '缓存状态获取成功',
            'data': stats
        })
    except Exception as e:
        logger.error(f"缓存状态检查失败: {e}")
        return Response({
            'code': 500,
            'message': '缓存状态检查失败',
            'error': str(e)
        }, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_cache(request):
    """清空指定类型的缓存"""
    try:
        data = request.data
        cache_type = data.get('type', 'all')  # all, animals, shelters, posts, users
        
        cleared_patterns = []
        
        if cache_type == 'all':
            # 清空所有缓存
            cache.clear()
            cleared_patterns.append('所有缓存')
        else:
            # 根据类型清空特定缓存
            patterns_map = {
                'animals': [
                    f"{CACHE_PREFIX['animal_list']}*",
                    f"{CACHE_PREFIX['animal_detail']}*"
                ],
                'shelters': [
                    f"{CACHE_PREFIX['shelter_list']}*",
                    f"{CACHE_PREFIX['shelter_detail']}*"
                ],
                'posts': [
                    f"{CACHE_PREFIX['post_list']}*",
                    f"{CACHE_PREFIX['post_detail']}*"
                ],
                'users': [
                    f"{CACHE_PREFIX['user_profile']}*"
                ],
                'statistics': [
                    f"{CACHE_PREFIX['statistics']}*"
                ]
            }
            
            patterns = patterns_map.get(cache_type, [])
            for pattern in patterns:
                invalidate_cache_pattern(pattern)
                cleared_patterns.append(pattern)
        
        return Response({
            'code': 200,
            'message': f'缓存清空成功: {", ".join(cleared_patterns)}'
        })
        
    except Exception as e:
        logger.error(f"缓存清空失败: {e}")
        return Response({
            'code': 500,
            'message': '缓存清空失败',
            'error': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def cache_stats(request):
    """获取缓存统计信息"""
    try:
        # 获取缓存中的关键数据
        stats = {}
        
        # 统计各类数据的数量
        from animals.models import Animal
        from shelters.models import Shelter
        from community.models import Post, Comment
        
        stats.update({
            'animals_total': Animal.objects.count(),
            'animals_available': Animal.objects.filter(status='available').count(),
            'shelters_total': Shelter.objects.count(),
            'posts_total': Post.objects.count(),
            'comments_total': Comment.objects.count(),
        })
        
        # 获取缓存中的统计数据（如果有）
        cached_stats = cache.get(f"{CACHE_PREFIX['statistics']}overview")
        if cached_stats:
            stats['cached_data'] = cached_stats
        
        return Response({
            'code': 200,
            'message': '统计信息获取成功',
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"统计信息获取失败: {e}")
        return Response({
            'code': 500,
            'message': '统计信息获取失败',
            'error': str(e)
        }, status=500)

# 缓存管理相关的URL配置建议添加到urls.py中：
"""
urlpatterns = [
    path('cache/status/', cache_status, name='cache_status'),
    path('cache/clear/', clear_cache, name='clear_cache'),
    path('cache/stats/', cache_stats, name='cache_stats'),
]
"""