from django.core.cache import cache
from django.conf import settings
from functools import wraps
import json
import logging

logger = logging.getLogger(__name__)

# 缓存键前缀常量
CACHE_PREFIX = {
    'animal_list': 'animals:list:',
    'animal_detail': 'animals:detail:',
    'shelter_list': 'shelters:list:',
    'shelter_detail': 'shelters:detail:',
    'post_list': 'posts:list:',
    'post_detail': 'posts:detail:',
    'user_profile': 'users:profile:',
    'statistics': 'stats:',
}

# 缓存时间配置（秒）
CACHE_TIMEOUT = {
    'short': 300,        # 5分钟 - 频繁变动数据
    'medium': 1800,      # 30分钟 - 中等频率更新数据
    'long': 7200,        # 2小时 - 较少变动数据
    'very_long': 86400,  # 24小时 - 很少变动数据
}

def get_cache_key(prefix, *args):
    """生成缓存键"""
    key_parts = [prefix.rstrip(':')]
    for arg in args:
        if isinstance(arg, (int, str)):
            key_parts.append(str(arg))
        elif hasattr(arg, 'pk'):
            key_parts.append(str(arg.pk))
    return ':'.join(key_parts)

def cache_result(timeout_key='medium', key_prefix=''):
    """
    缓存函数结果的装饰器
    
    Args:
        timeout_key: 超时时间键 ('short', 'medium', 'long', 'very_long')
        key_prefix: 缓存键前缀
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = get_cache_key(key_prefix, *args, **kwargs)
            
            # 尝试从缓存获取
            result = cache.get(cache_key)
            if result is not None:
                # 缓存命中日志
                return result
            
            # 执行原函数
            result = func(*args, **kwargs)
            
            # 缓存结果
            timeout = CACHE_TIMEOUT.get(timeout_key, CACHE_TIMEOUT['medium'])
            cache.set(cache_key, result, timeout)
            # 缓存设置日志
            
            return result
        return wrapper
    return decorator

def invalidate_cache_pattern(pattern):
    """
    根据模式删除缓存
    
    Args:
        pattern: 缓存键模式，如 'animals:list:*'
    """
    try:
        # 获取所有匹配的键
        keys = cache.keys(pattern)
        if keys:
            cache.delete_many(keys)
            logger.info(f"删除缓存键: {len(keys)} 个 ({pattern})")
    except Exception as e:
        logger.error(f"删除缓存失败: {e}")

def invalidate_related_caches(instance):
    """
    根据模型实例删除相关缓存
    
    Args:
        instance: 模型实例
    """
    model_name = instance.__class__.__name__.lower()
    
    if model_name == 'animal':
        # 删除动物相关缓存
        invalidate_cache_pattern(f"{CACHE_PREFIX['animal_list']}*")
        invalidate_cache_pattern(f"{CACHE_PREFIX['animal_detail']}{instance.pk}")
    elif model_name == 'shelter':
        # 删除基地相关缓存
        invalidate_cache_pattern(f"{CACHE_PREFIX['shelter_list']}*")
        invalidate_cache_pattern(f"{CACHE_PREFIX['shelter_detail']}{instance.pk}")
    elif model_name == 'post':
        # 删除帖子相关缓存
        invalidate_cache_pattern(f"{CACHE_PREFIX['post_list']}*")
        invalidate_cache_pattern(f"{CACHE_PREFIX['post_detail']}{instance.pk}")

def get_or_set_cache(key, callback, timeout=CACHE_TIMEOUT['medium']):
    """
    获取或设置缓存的便捷函数
    
    Args:
        key: 缓存键
        callback: 当缓存不存在时调用的函数
        timeout: 超时时间
    
    Returns:
        缓存的值
    """
    def wrapper():
        return callback()
    
    return cache.get_or_set(key, wrapper, timeout)

# 常用缓存装饰器预设
cache_animal_list = cache_result('long', CACHE_PREFIX['animal_list'])
cache_animal_detail = cache_result('medium', CACHE_PREFIX['animal_detail'])
cache_shelter_list = cache_result('long', CACHE_PREFIX['shelter_list'])
cache_shelter_detail = cache_result('medium', CACHE_PREFIX['shelter_detail'])
cache_post_list = cache_result('medium', CACHE_PREFIX['post_list'])
cache_post_detail = cache_result('short', CACHE_PREFIX['post_detail'])
cache_user_profile = cache_result('long', CACHE_PREFIX['user_profile'])
cache_statistics = cache_result('very_long', CACHE_PREFIX['statistics'])