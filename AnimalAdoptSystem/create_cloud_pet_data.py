"""
创建云养宠物动态测试数据
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from adoptions.models import AdoptionApplication, CloudPetActivity
from animals.models import Animal
from users.models import User
from datetime import datetime, timedelta
import random

def create_cloud_pet_activities():
    """为已领养的动物创建云养动态"""
    
    # 获取所有已审核通过的领养申请
    approved_applications = AdoptionApplication.objects.filter(
        status__in=['approved', 'completed']
    ).select_related('animal', 'applicant')
    
    if not approved_applications.exists():
        print("❌ 没有找到已审核通过的领养申请")
        return
    
    print(f"✅ 找到 {approved_applications.count()} 个已审核通过的领养申请")
    
    # 活动类型和示例内容
    activity_templates = {
        'feeding': [
            ('早餐时间', '今天给{animal}准备了营养丰富的早餐，它吃得很开心！'),
            ('午餐时光', '{animal}今天的午餐是特制的猫/狗粮，吃得津津有味。'),
            ('晚餐记录', '傍晚时分，{animal}享用了一顿美味的晚餐。'),
        ],
        'medical': [
            ('疫苗接种', '{animal}今天完成了疫苗接种，健康状况良好。'),
            ('体检报告', '{animal}进行了定期体检，各项指标正常。'),
            ('驱虫护理', '今天给{animal}做了体内外驱虫，保护它的健康。'),
        ],
        'playing': [
            ('游戏时间', '{animal}今天在草地上玩得很开心，追逐小球。'),
            ('互动玩耍', '工作人员陪{animal}一起玩耍，它非常活跃。'),
            ('探索新环境', '{animal}对新玩具充满好奇，玩得不亦乐乎。'),
        ],
        'grooming': [
            ('美容护理', '今天给{animal}洗了个澡，梳理了毛发，变得干干净净。'),
            ('修剪指甲', '{animal}配合地完成了指甲修剪，表现很棒。'),
            ('毛发护理', '专业美容师为{animal}进行了毛发护理。'),
        ],
        'exercise': [
            ('晨间散步', '{animal}今天早上在园区内散步，呼吸新鲜空气。'),
            ('户外运动', '{animal}参加了户外活动，运动量充足。'),
            ('跑步训练', '今天{animal}进行了跑步训练，体力很好。'),
        ],
        'other': [
            ('日常记录', '{animal}今天状态良好，在基地里悠闲地度过了一天。'),
            ('新朋友', '{animal}认识了新朋友，相处融洽。'),
            ('温馨时刻', '{animal}在阳光下晒太阳，看起来非常惬意。'),
        ],
    }
    
    created_count = 0
    
    for app in approved_applications:
        animal = app.animal
        
        # 为每个动物创建5-15条动态
        num_activities = random.randint(5, 15)
        
        # 从审核通过日期开始
        start_date = app.reviewed_at.date() if app.reviewed_at else datetime.now().date() - timedelta(days=30)
        
        print(f"\n🐾 为 {animal.name} 创建 {num_activities} 条动态...")
        
        for i in range(num_activities):
            # 随机选择活动类型
            activity_type = random.choice(list(activity_templates.keys()))
            
            # 随机选择一个模板
            template = random.choice(activity_templates[activity_type])
            title, content_template = template
            
            # 替换动物名称
            content = content_template.format(animal=animal.name)
            
            # 计算日期（从审核日期开始，每隔几天一条）
            days_offset = (num_activities - i) * random.randint(1, 3)
            activity_date = start_date + timedelta(days=days_offset)
            
            # 确保不超过当前日期
            if activity_date > datetime.now().date():
                activity_date = datetime.now().date() - timedelta(days=random.randint(0, 5))
            
            # 创建动态
            activity = CloudPetActivity.objects.create(
                animal=animal,
                activity_type=activity_type,
                title=title,
                content=content,
                images=[],  # 可以后续添加图片URL
                created_by=None,  # 基地管理员发布
                created_at=datetime.combine(activity_date, datetime.min.time()) + timedelta(hours=random.randint(8, 18))
            )
            
            created_count += 1
    
    print(f"\n✅ 成功创建 {created_count} 条云养宠物动态")

if __name__ == '__main__':
    print("🚀 开始创建云养宠物动态测试数据...\n")
    create_cloud_pet_activities()
    print("\n✨ 完成！")
