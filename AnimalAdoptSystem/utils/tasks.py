from celery import shared_task
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

@shared_task
def clear_cache():
    """清理缓存任务"""
    try:
        # 清理所有缓存
        cache.clear()
        logger.info('缓存清理完成')
        return '缓存清理成功'
    except Exception as e:
        logger.error(f'缓存清理失败: {str(e)}')
        return f'缓存清理失败: {str(e)}'

@shared_task
def health_check():
    """系统健康检查任务"""
    try:
        # 检查数据库连接
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        
        # 检查缓存
        cache.set('health_check', 'ok', 30)
        cache_result = cache.get('health_check')
        
        status = {
            'database': 'OK' if result else 'ERROR',
            'cache': 'OK' if cache_result else 'ERROR',
            'timestamp': str(cache.timeout)
        }
        
        logger.info(f'健康检查完成: {status}')
        return f'健康检查完成: {status}'
    except Exception as e:
        logger.error(f'健康检查失败: {str(e)}')
        return f'健康检查失败: {str(e)}'

@shared_task
def process_image_analysis(image_data, analysis_type='breed'):
    """处理图像分析任务（与百度AI集成）"""
    try:
        from utils.baidu_ai import baidu_ai_helper
        
        if analysis_type == 'breed':
            result = baidu_ai_helper.identify_animal_breed(image_data)
        elif analysis_type == 'health':
            result = baidu_ai_helper.analyze_animal_health(image_data)
        else:
            result = {'error': '未知的分析类型'}
        
        logger.info(f'图像分析完成: {result}')
        return f'图像分析成功: {result}'
    except Exception as e:
        logger.error(f'图像分析失败: {str(e)}')
        return f'图像分析失败: {str(e)}'