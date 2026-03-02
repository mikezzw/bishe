import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from volunteers.models import VolunteerActivity

# 检查所有活动
activities = VolunteerActivity.objects.all()
print(f'总共有 {activities.count()} 个活动')

for activity in activities:
    print(f'活动: {activity.name}')
    print(f'  ID: {activity.id}')
    print(f'  状态: {activity.status}')
    print(f'  组织者: {activity.organizer.username}')
    print(f'  基地: {activity.shelter.name if activity.shelter else "无"}')
    print(f'  创建时间: {activity.created_at}')
    print()
