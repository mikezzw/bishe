import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client

def test_get_user_shelter_api():
    """测试get_user_shelter API是否正确返回基地信息"""
    print("=== 测试get_user_shelter API ===")
    
    # 创建测试客户端
    client = Client()
    
    # 测试用户ID为2的基地信息
    user_id = 2
    response = client.get(f'/api/shelters/staff/user/{user_id}/shelter/')
    
    print(f"API响应状态码: {response.status_code}")
    print(f"API响应数据: {response.json()}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('code') == 200 and data.get('data'):
            shelters = data.get('data')
            print(f"\n成功获取到 {len(shelters)} 个基地:")
            for item in shelters:
                shelter = item.get('shelter')
                role = item.get('role')
                print(f"- 基地名称: {shelter.get('name')}, 角色: {role}")
                print(f"  基地地址: {shelter.get('address')}")
                print(f"  联系人: {shelter.get('contact_name')}")
                print(f"  联系电话: {shelter.get('contact_phone')}")
                print(f"  邮箱: {shelter.get('email')}")
                print(f"  容纳能力: {shelter.get('capacity')}")
                print(f"  描述: {shelter.get('description')}")
        else:
            print("API返回了错误响应")
    else:
        print(f"API请求失败，状态码: {response.status_code}")
        print(f"错误信息: {response.content}")

if __name__ == "__main__":
    test_get_user_shelter_api()
