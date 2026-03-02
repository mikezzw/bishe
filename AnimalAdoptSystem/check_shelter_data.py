import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from users.models import User
from shelters.models import Shelter, ShelterStaff

def check_user_shelter_relation():
    """检查用户与基地的关联关系"""
    print("=== 检查用户与基地的关联关系 ===")
    
    # 获取所有基地管理员用户
    shelter_users = User.objects.filter(user_type='shelter')
    print(f"共有 {shelter_users.count()} 个基地管理员用户")
    
    for user in shelter_users:
        print(f"\n用户ID: {user.id}, 用户名: {user.username}, 邮箱: {user.email}")
        print(f"User模型关联的基地: {user.shelter.name if user.shelter else '无'}")
        
        # 检查ShelterStaff记录
        staff_records = ShelterStaff.objects.filter(user=user)
        print(f"ShelterStaff记录数量: {staff_records.count()}")
        
        for record in staff_records:
            print(f"  基地ID: {record.shelter.id}, 基地名称: {record.shelter.name}, 角色: {record.role}")
            
            # 检查基地数据完整性
            shelter = record.shelter
            print(f"  基地数据完整性:")
            print(f"    名称: {shelter.name if shelter.name else '空'}")
            print(f"    地址: {shelter.address if shelter.address else '空'}")
            print(f"    联系人: {shelter.contact_name if shelter.contact_name else '空'}")
            print(f"    联系电话: {shelter.contact_phone if shelter.contact_phone else '空'}")
            print(f"    邮箱: {shelter.email if shelter.email else '空'}")
            print(f"    容纳能力: {shelter.capacity if shelter.capacity else '空'}")
            print(f"    描述: {shelter.description if shelter.description else '空'}")

def check_all_shelters():
    """检查所有基地的数据完整性"""
    print("\n=== 检查所有基地的数据完整性 ===")
    
    shelters = Shelter.objects.all()
    print(f"共有 {shelters.count()} 个基地")
    
    for shelter in shelters:
        print(f"\n基地ID: {shelter.id}, 名称: {shelter.name}")
        print(f"  地址: {shelter.address if shelter.address else '空'}")
        print(f"  联系人: {shelter.contact_name if shelter.contact_name else '空'}")
        print(f"  联系电话: {shelter.contact_phone if shelter.contact_phone else '空'}")
        print(f"  邮箱: {shelter.email if shelter.email else '空'}")
        print(f"  容纳能力: {shelter.capacity if shelter.capacity else '空'}")
        print(f"  描述: {shelter.description if shelter.description else '空'}")
        print(f"  状态: {shelter.status if shelter.status else '空'}")

if __name__ == "__main__":
    check_user_shelter_relation()
    check_all_shelters()
