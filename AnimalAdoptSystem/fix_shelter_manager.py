import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from users.models import User
from shelters.models import Shelter, ShelterStaff

def check_shelter_managers():
    """检查基地管理员匹配情况"""
    print("=== 检查基地管理员匹配情况 ===")
    
    # 获取所有基地
    shelters = Shelter.objects.all()
    print(f"总共有 {shelters.count()} 个基地")
    
    issues = []
    
    for shelter in shelters:
        print(f"\n基地: {shelter.name} (ID: {shelter.id})")
        
        # 检查User模型中的manager关系
        manager_user = getattr(shelter, 'manager', None)
        if manager_user:
            print(f"  从User.shelter字段找到管理员: {manager_user.username} (ID: {manager_user.id})")
        else:
            print(f"  ❌ 未找到管理员 (User.shelter字段为空)")
            issues.append(f"基地 {shelter.name} 缺少管理员")
        
        # 检查ShelterStaff中的管理员
        staff_managers = ShelterStaff.objects.filter(shelter=shelter, role='manager')
        if staff_managers.exists():
            print(f"  从ShelterStaff找到管理员: {[sm.user.username for sm in staff_managers]}")
        else:
            print(f"  ❌ 未在ShelterStaff中找到管理员")
            if manager_user:
                issues.append(f"基地 {shelter.name} 的管理员 {manager_user.username} 未在ShelterStaff中记录")
        
        # 检查两者是否一致
        if manager_user and staff_managers.exists():
            staff_manager_usernames = [sm.user.username for sm in staff_managers]
            if manager_user.username not in staff_manager_usernames:
                print(f"  ❌ 管理员不匹配: User.shelter中的管理员 {manager_user.username} 不在ShelterStaff的管理员列表中")
                issues.append(f"基地 {shelter.name} 的管理员不匹配")
    
    print(f"\n=== 检查完成 ===")
    print(f"发现 {len(issues)} 个问题")
    for issue in issues:
        print(f"- {issue}")
    
    return issues

def fix_shelter_managers():
    """修复基地管理员匹配问题"""
    print("\n=== 开始修复基地管理员匹配问题 ===")
    
    shelters = Shelter.objects.all()
    fixed = 0
    
    for shelter in shelters:
        # 获取User模型中的管理员
        manager_user = getattr(shelter, 'manager', None)
        
        if manager_user:
            # 检查ShelterStaff中是否已有该管理员记录
            existing_staff = ShelterStaff.objects.filter(shelter=shelter, user=manager_user).first()
            
            if not existing_staff:
                # 创建ShelterStaff记录
                ShelterStaff.objects.create(
                    shelter=shelter,
                    user=manager_user,
                    role='manager'
                )
                print(f"✅ 为基地 {shelter.name} 创建了管理员 {manager_user.username} 的ShelterStaff记录")
                fixed += 1
            elif existing_staff.role != 'manager':
                # 更新角色为管理员
                existing_staff.role = 'manager'
                existing_staff.save()
                print(f"✅ 更新基地 {shelter.name} 的 {manager_user.username} 角色为管理员")
                fixed += 1
            else:
                print(f"ℹ️ 基地 {shelter.name} 的管理员 {manager_user.username} 记录已存在且正确")
        else:
            print(f"⚠️ 基地 {shelter.name} 没有设置管理员，跳过")
    
    print(f"\n=== 修复完成 ===")
    print(f"修复了 {fixed} 个问题")

if __name__ == "__main__":
    issues = check_shelter_managers()
    if issues:
        input("\n按回车键开始修复...")
        fix_shelter_managers()
    else:
        print("\n没有发现问题，无需修复")
