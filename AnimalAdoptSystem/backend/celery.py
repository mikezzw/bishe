import os
from celery import Celery
from django.conf import settings

# 设置 Django 的默认设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# 创建 Celery 应用实例
app = Celery('AnimalAdoptSystem')

# 使用 Django 的设置文件配置 Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动从所有已注册的 Django app 中发现任务
app.autodiscover_tasks()

# 可选：添加一些调试信息
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')