import requests
import base64
import json
from django.conf import settings

class BaiduAIHelper:
    """百度AI工具类"""
    
    def __init__(self):
        self.api_key = settings.BAIDU_AI_CONFIG['API_KEY']
        self.secret_key = settings.BAIDU_AI_CONFIG['SECRET_KEY']
        self.animal_detect_url = settings.BAIDU_AI_CONFIG['ANIMAL_DETECT_URL']
        self.access_token = None
    
    def get_access_token(self):
        """获取百度AI访问令牌"""
        if self.access_token:
            return self.access_token
            
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            'grant_type': 'client_credentials',
            'client_id': self.api_key,
            'client_secret': self.secret_key
        }
        
        try:
            response = requests.post(url, params=params)
            result = response.json()
            if 'access_token' in result:
                self.access_token = result['access_token']
                return self.access_token
            else:
                raise Exception(f"获取access_token失败: {result}")
        except Exception as e:
            raise Exception(f"获取access_token异常: {str(e)}")
    
    def identify_animal_breed(self, image_data):
        """
        识别动物品种
        Args:
            image_data: 图片数据（bytes或base64字符串）
        Returns:
            dict: 识别结果
        """
        try:
            # 获取access_token
            access_token = self.get_access_token()
            
            # 处理图片数据
            if isinstance(image_data, bytes):
                image_base64 = base64.b64encode(image_data).decode('utf-8')
            elif isinstance(image_data, str) and image_data.startswith('data:image'):
                # 如果是data URL格式，提取base64部分
                image_base64 = image_data.split(',')[1]
            else:
                image_base64 = image_data
            
            # 构造请求参数
            params = {
                'image': image_base64,
                'access_token': access_token
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            # 发送请求
            response = requests.post(
                self.animal_detect_url,
                data=params,
                headers=headers
            )
            
            result = response.json()
            
            # 解析结果
            if 'result' in result and len(result['result']) > 0:
                animal_info = result['result'][0]
                return {
                    'success': True,
                    'breed': animal_info.get('name', '未知品种'),
                    'confidence': animal_info.get('score', 0),
                    'baike_info': animal_info.get('baike_info', {}),
                    'raw_result': result
                }
            else:
                return {
                    'success': False,
                    'error': '未能识别出动物品种',
                    'raw_result': result
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'识别失败: {str(e)}'
            }

    
    def identify_from_url(self, image_url):
        """
        从URL识别动物品种
        Args:
            image_url: 图片URL
        Returns:
            dict: 识别结果
        """
        try:
            # 下载图片
            response = requests.get(image_url)
            response.raise_for_status()
            image_data = response.content
            return self.identify_animal_breed(image_data)
        except Exception as e:
            return {
                'success': False,
                'error': f'下载图片失败: {str(e)}'
            }

# 单例实例
baidu_ai_helper = BaiduAIHelper()