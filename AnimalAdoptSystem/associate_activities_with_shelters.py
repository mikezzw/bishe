import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from volunteers.models import VolunteerActivity
from shelters.models import Shelter

# 获取第一个基地
shelter = Shelter.objects.first()
if not shelter:
    print('没有找到基地')
    exit()

print(f'找到基地: {shelter.name} (ID: {shelter.id})')

# 为所有活动关联这个基地
activities = VolunteerActivity.objects.all()
for activity in activities:
    activity.shelter = shelter
    activity.save()
    print(f'已为活动 "{activity.name}" 关联基地 "{shelter.name}"')

print(f'已为 {activities.count()} 个活动关联基地')
