from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

@shared_task
def cleanup_expired_notifications():
    """清理过期的通知消息"""
    try:
        # 假设我们有一个 Notification 模型
        # 这里是示例代码，你需要根据实际模型调整
        from community.models import Notification
        
        # 删除30天前的通知
        expiry_date = timezone.now() - timedelta(days=30)
        expired_count = Notification.objects.filter(
            created_at__lt=expiry_date
        ).count()
        
        Notification.objects.filter(
            created_at__lt=expiry_date
        ).delete()
        
        logger.info(f'清理了 {expired_count} 条过期通知')
        return f'成功清理 {expired_count} 条过期通知'
    except Exception as e:
        logger.error(f'清理过期通知失败: {str(e)}')
        return f'清理失败: {str(e)}'

@shared_task
def send_daily_summary():
    """发送每日摘要邮件"""
    try:
        from users.models import User
        from animals.models import Animal
        from adoptions.models import AdoptionApplication
        
        # 获取今日统计数据
        today = timezone.now().date()
        new_animals = Animal.objects.filter(created_at__date=today).count()
        new_applications = AdoptionApplication.objects.filter(created_at__date=today).count()
        active_users = User.objects.filter(last_login__date=today).count()
        
        # 构造邮件内容
        subject = f'[{today}] 平台运营日报'
        message = f'''
        动物领养平台运营日报 - {today}
        
        📊 今日数据统计：
        • 新增动物：{new_animals} 只
        • 新领养申请：{new_applications} 份
        • 活跃用户：{active_users} 人
        
        🎯 重点关注事项：
        • 待审核领养申请：{AdoptionApplication.objects.filter(status='pending').count()} 份
        • 待处理互动申请：{0} 份  # 需要根据实际模型调整
        
        感谢您的辛勤工作！
        
        此致
        动物领养平台管理系统
        '''
        
        # 发送给管理员（这里需要根据你的管理员标识调整）
        admin_emails = User.objects.filter(is_staff=True).values_list('email', flat=True)
        if admin_emails:
            from django.core.mail import send_mail
            from django.conf import settings
            
            send_mail(
                subject, 
                message, 
                settings.DEFAULT_FROM_EMAIL, 
                list(admin_emails)
            )
            logger.info(f'日报邮件已发送给 {len(admin_emails)} 位管理员')
            return f'日报邮件发送成功，收件人: {len(admin_emails)} 人'
        else:
            return '没有找到管理员邮箱'
            
    except Exception as e:
        logger.error(f'发送日报邮件失败: {str(e)}')
        return f'日报发送失败: {str(e)}'