import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from shelters.models import Shelter

def check_shelter_info():
    """检查基地信息"""
    print("=== 检查基地信息 ===")
    
    # 获取所有基地
    shelters = Shelter.objects.all()
    print(f"总共有 {shelters.count()} 个基地")
    
    for shelter in shelters:
        print(f"\n基地ID: {shelter.id}")
        print(f"  名称: {shelter.name}")
        print(f"  描述: {shelter.description[:50]}..." if len(shelter.description) > 50 else f"  描述: {shelter.description}")
        print(f"  地址: {shelter.address}")
        print(f"  联系人: {shelter.contact_name}")
        print(f"  联系电话: {shelter.contact_phone}")
        print(f"  邮箱: {shelter.email}")

if __name__ == "__main__":
    check_shelter_info()
