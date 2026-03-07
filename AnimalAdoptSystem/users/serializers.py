import base64
import re
from rest_framework import serializers
from .models import User
from shelters.models import Shelter

class UserSerializer(serializers.ModelSerializer):
    shelter = serializers.SerializerMethodField()
    
    def get_shelter(self, obj):
        if obj.shelter:
            from shelters.serializers import ShelterSerializer
            return ShelterSerializer(obj.shelter).data
        return None
    
    # 添加对 Base64 头像的支持
    avatar = serializers.SerializerMethodField()
    
    def get_avatar(self, obj):
        """返回头像的完整 URL"""
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None
    
    def to_internal_value(self, data):
        """处理传入的数据，支持 Base64 图片"""
        ret = super().to_internal_value(data)
        
        # 如果 avatar 字段是 Base64 字符串，需要特殊处理
        if 'avatar' in data and isinstance(data['avatar'], str):
            avatar_data = data['avatar']
            
            # 检查是否为 Base64 格式
            if avatar_data.startswith('data:image'):
                # 这是一个 Base64 图片，暂时存储到 validated_data 中
                # 实际的文件处理将在视图或 create/update 方法中进行
                ret['avatar_base64'] = avatar_data
        
        return ret
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'user_type', 'phone', 'avatar', 'address', 'bio', 'shelter', 'created_at',
                  'openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism')

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    password2 = serializers.CharField(write_only=True, required=True, min_length=6)
    # 基地注册字段
    shelter_name = serializers.CharField(write_only=True, required=False)
    shelter_address = serializers.CharField(write_only=True, required=False)
    shelter_contact_name = serializers.CharField(write_only=True, required=False)
    shelter_description = serializers.CharField(write_only=True, required=False)
    shelter_capacity = serializers.IntegerField(write_only=True, required=False, min_value=1)
    shelter_qr_code = serializers.CharField(write_only=True, required=False)  # Base64 字符串

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'user_type', 'phone',
                  'shelter_name', 'shelter_address', 'shelter_contact_name', 'shelter_description', 'shelter_capacity', 'shelter_qr_code')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "两次输入的密码不一致"})
        
        # 验证基地注册字段
        if attrs.get('user_type') == 'shelter':
            if not all([attrs.get('shelter_name'), attrs.get('shelter_address'), 
                       attrs.get('shelter_contact_name'), attrs.get('shelter_capacity')]):
                raise serializers.ValidationError({"shelter": "请填写完整的基地信息"})
        
        return attrs

    def create(self, validated_data):
        # 提取基地注册字段
        shelter_name = validated_data.pop('shelter_name', None)
        shelter_address = validated_data.pop('shelter_address', None)
        shelter_contact_name = validated_data.pop('shelter_contact_name', None)
        shelter_description = validated_data.pop('shelter_description', '')
        shelter_capacity = validated_data.pop('shelter_capacity', None)
        shelter_qr_code = validated_data.pop('shelter_qr_code', None)  # Base64 字符串
        user_type = validated_data.pop('user_type', 'normal')
        phone = validated_data.pop('phone', None)
        
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        
        # 设置用户类型和电话
        user.user_type = user_type
        user.phone = phone
        
        # 如果是基地用户，创建对应的基地记录
        if user_type == 'shelter' and shelter_name:
            # 准备创建基地的数据
            shelter_data = {
                'name': shelter_name,
                'description': shelter_description,
                'address': shelter_address,
                'contact_name': shelter_contact_name,
                'contact_phone': phone,
                'email': validated_data['email'],
                'capacity': shelter_capacity,
            }
            
            # 如果有上传收款码（Base64），添加到数据中
            if shelter_qr_code:
                # 将 Base64 字符串存储为数组
                shelter_data['qr_code'] = [shelter_qr_code]
            
            # 创建基地
            shelter = Shelter.objects.create(**shelter_data)
            user.shelter = shelter
        
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("该邮箱未注册")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    verification_code = serializers.CharField(required=True, max_length=6)
    new_password = serializers.CharField(required=True, min_length=6)
    confirm_password = serializers.CharField(required=True, min_length=6)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "两次输入的密码不一致"})
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)
    confirm_password = serializers.CharField(required=True, min_length=6)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "两次输入的密码不一致"})
        return attrs
