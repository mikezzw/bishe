from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging
import csv
from io import StringIO

logger = logging.getLogger(__name__)

@shared_task
def generate_daily_report():
    """生成每日运营报告"""
    try:
        from users.models import User
        from animals.models import Animal
        from adoptions.models import AdoptionApplication
        from shelters.models import Shelter
        
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # 收集统计数据
        report_data = {
            'date': today,
            'new_users': User.objects.filter(date_joined__date=yesterday).count(),
            'new_animals': Animal.objects.filter(created_at__date=yesterday).count(),
            'new_applications': AdoptionApplication.objects.filter(created_at__date=yesterday).count(),
            'total_animals': Animal.objects.count(),
            'total_users': User.objects.count(),
            'total_shelters': Shelter.objects.count(),
            'pending_applications': AdoptionApplication.objects.filter(status='pending').count(),
        }
        
        # 记录日志
        logger.info(f"生成日报: {report_data}")
        return f'日报生成成功: {report_data}'
        
    except Exception as e:
        logger.error(f'生成日报失败: {str(e)}')
        return f'日报生成失败: {str(e)}'

@shared_task
def backup_database():
    """数据库备份任务"""
    try:
        import subprocess
        import os
        from django.conf import settings
        
        # 创建备份目录
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # 生成备份文件名
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'db_backup_{timestamp}.sql')
        
        # 执行备份命令（SQLite示例）
        if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
            db_path = settings.DATABASES['default']['NAME']
            # 简单的文件复制作为备份
            import shutil
            shutil.copy2(db_path, backup_file)
            
        logger.info(f'数据库备份完成: {backup_file}')
        return f'备份成功: {backup_file}'
        
    except Exception as e:
        logger.error(f'数据库备份失败: {str(e)}')
        return f'备份失败: {str(e)}'

@shared_task
def send_weekly_statistics():
    """发送每周统计报告"""
    try:
        from users.models import User
        from animals.models import Animal
        from adoptions.models import AdoptionApplication
        from django.core.mail import send_mail
        from django.conf import settings
        
        # 统计最近7天的数据
        week_ago = timezone.now() - timedelta(days=7)
        
        weekly_stats = {
            'new_users': User.objects.filter(date_joined__gte=week_ago).count(),
            'new_animals': Animal.objects.filter(created_at__gte=week_ago).count(),
            'new_applications': AdoptionApplication.objects.filter(created_at__gte=week_ago).count(),
            'completed_adoptions': AdoptionApplication.objects.filter(
                status='completed', 
                updated_at__gte=week_ago
            ).count(),
        }
        
        # 构造邮件内容
        subject = f'[{timezone.now().date()}] 平台周报'
        message = f'''
        动物领养平台周报
        
        📊 本周数据统计：
        • 新增用户：{weekly_stats['new_users']} 人
        • 新增动物：{weekly_stats['new_animals']} 只
        • 新领养申请：{weekly_stats['new_applications']} 份
        • 成功领养：{weekly_stats['completed_adoptions']} 只
        
        🎉 感谢所有用户的积极参与！
        
        此致
        动物领养平台团队
        '''
        
        # 发送给相关用户
        admin_users = User.objects.filter(is_staff=True)
        if admin_users.exists():
            recipient_list = list(admin_users.values_list('email', flat=True))
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
            logger.info(f'周报邮件已发送给 {len(recipient_list)} 位管理员')
            return f'周报发送成功，收件人: {len(recipient_list)} 人'
        else:
            return '没有找到管理员用户'
            
    except Exception as e:
        logger.error(f'发送周报失败: {str(e)}')
        return f'周报发送失败: {str(e)}'