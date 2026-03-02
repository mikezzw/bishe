from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import User
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_welcome_email(user_id):
    """发送欢迎邮件任务"""
    try:
        user = User.objects.get(id=user_id)
        subject = '欢迎加入动物领养平台'
        message = f'''
        亲爱的 {user.username}，
        
        欢迎您加入我们的动物领养平台！
        
        在这里您可以：
        - 浏览可爱的待领养动物
        - 提交领养申请
        - 参与志愿者活动
        - 与其他爱心人士交流
        
        祝您在平台上有一个愉快的体验！
        
        此致
        动物领养平台团队
        '''
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]
        
        send_mail(subject, message, from_email, recipient_list)
        logger.info(f'欢迎邮件已发送给用户 {user.username}')
        return f'邮件发送成功: {user.email}'
    except User.DoesNotExist:
        logger.error(f'用户 ID {user_id} 不存在')
        return f'用户不存在: {user_id}'
    except Exception as e:
        logger.error(f'发送邮件失败: {str(e)}')
        return f'邮件发送失败: {str(e)}'

@shared_task
def send_adoption_status_update(user_id, adoption_id, status):
    """发送领养状态更新通知"""
    try:
        user = User.objects.get(id=user_id)
        status_map = {
            'approved': '审核通过',
            'rejected': '审核拒绝',
            'completed': '领养完成',
            'cancelled': '申请取消'
        }
        
        subject = f'领养申请状态更新 - {status_map.get(status, status)}'
        message = f'''
        亲爱的 {user.username}，
        
        您的领养申请(ID: {adoption_id})状态已更新为：{status_map.get(status, status)}
        
        请及时登录平台查看详情。
        
        此致
        动物领养平台团队
        '''
        
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        logger.info(f'领养状态更新邮件已发送给用户 {user.username}')
        return f'状态更新邮件发送成功: {user.email}'
    except Exception as e:
        logger.error(f'发送状态更新邮件失败: {str(e)}')
        return f'邮件发送失败: {str(e)}'

@shared_task
def cleanup_inactive_users():
    """清理长期未激活的用户账户"""
    try:
        from django.utils import timezone
        from datetime import timedelta
        
        # 查找30天内未激活的用户
        inactive_threshold = timezone.now() - timedelta(days=30)
        inactive_users = User.objects.filter(
            is_active=False,
            date_joined__lt=inactive_threshold
        )
        
        count = inactive_users.count()
        inactive_users.delete()
        
        logger.info(f'清理了 {count} 个长期未激活的用户账户')
        return f'成功清理 {count} 个_inactive用户'
    except Exception as e:
        logger.error(f'清理_inactive用户失败: {str(e)}')
        return f'清理失败: {str(e)}'