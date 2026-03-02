import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from users.models import User
from shelters.models import Shelter, ShelterStaff

def check_user_shelters(username):
    """检查用户关联的基地"""
    print(f"=== 检查用户 {username} 的基地关联情况 ===")
    
    # 查找用户
    try:
        user = User.objects.get(username=username)
        print(f"用户ID: {user.id}")
        print(f"用户类型: {user.user_type}")
        print(f"用户管理的基地: {user.shelter.name if user.shelter else '无'}")
        
        # 检查ShelterStaff中的记录
        staff_records = ShelterStaff.objects.filter(user=user)
        print(f"\n用户在ShelterStaff中的记录: {staff_records.count()} 条")
        
        for record in staff_records:
            print(f"  基地: {record.shelter.name} (ID: {record.shelter.id})")
            print(f"  角色: {record.get_role_display()}")
            print()
        
        return staff_records
    except User.DoesNotExist:
        print(f"用户 {username} 不存在")
        return []

if __name__ == "__main__":
    # 检查用户"111"的基地关联情况
    check_user_shelters("111")
