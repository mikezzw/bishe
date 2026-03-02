import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from shelters.models import Shelter

# 检查所有基地
shelters = Shelter.objects.all()
print(f'总共有 {shelters.count()} 个基地')

for shelter in shelters:
    print(f'基地: {shelter.name}')
    print(f'  ID: {shelter.id}')
    print(f'  地址: {shelter.address}')
    print(f'  联系电话: {shelter.phone}')
    print()
