from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.files.base import ContentFile
import base64
import re
from .models import User
from .serializers import UserSerializer, UserRegisterSerializer, UserLoginSerializer, \
    PasswordResetSerializer, PasswordResetConfirmSerializer, PasswordChangeSerializer
from volunteers.models import VolunteerProfile

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['register', 'login', 'password_reset', 'password_reset_confirm']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'code': 200,
                'message': '注册成功',
                'data': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'code': 400,
            'message': '注册失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'code': 200,
                    'message': '登录成功',
                    'data': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                        'user': UserSerializer(user).data
                    }
                })
            return Response({
                'code': 401,
                'message': '用户名或密码错误'
            }, status=status.HTTP_401_UNAUTHORIZED)
        return Response({
            'code': 400,
            'message': '请求参数错误',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='profile')
    def profile(self, request):
        user = request.user
        return Response({
            'code': 200,
            'message': '获取个人信息成功',
            'data': UserSerializer(user).data
        })

    @action(detail=False, methods=['put'], url_path='profile')
    def update_profile(self, request):
        user = request.user
        data = request.data.copy()
        
        # 处理 Base64 头像
        if 'avatar_base64' in data or ('avatar' in data and isinstance(data.get('avatar'), str) and data['avatar'].startswith('data:image')):
            avatar_base64 = data.get('avatar_base64') or data.get('avatar')
            
            try:
                # 解析 Base64 图片数据
                format_match = re.search(r'data:image/(\w+);base64,', avatar_base64)
                if not format_match:
                    return Response({
                        'code': 400,
                        'message': '无效的圖片格式'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                image_format = format_match.group(1)
                # 移除 Base64 头部，获取实际数据
                image_data = base64.b64decode(avatar_base64.split(',')[1])
                
                # 创建文件名
                filename = f'user_{user.id}_avatar.{image_format}'
                
                # 删除旧的头像文件（如果存在）
                if user.avatar:
                    user.avatar.delete(save=False)
                
                # 保存新头像
                user.avatar.save(
                    filename,
                    ContentFile(image_data),
                    save=True
                )
                
                # 从数据中移除 avatar_base64，避免重复处理
                if 'avatar_base64' in data:
                    del data['avatar_base64']
                if 'avatar' in data:
                    del data['avatar']
                    
            except Exception as e:
                return Response({
                    'code': 500,
                    'message': f'图片处理失败：{str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # 使用更新后的数据序列化用户
        serializer = UserSerializer(user, data=data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                'code': 200,
                'message': '更新个人信息成功',
                'data': serializer.data
            })
        return Response({
            'code': 400,
            'message': '更新失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='password-reset')
    def password_reset(self, request):
        """发送密码重置验证码"""
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            # 这里应该发送邮件验证码，暂时用固定验证码演示
            # 实际应用中应该生成随机验证码并发送邮件
            verification_code = "123456"  # 演示用验证码
            
            return Response({
                'code': 200,
                'message': '验证码已发送至您的邮箱',
                'data': {
                    'verification_code': verification_code  # 开发环境显示验证码
                }
            })
        return Response({
            'code': 400,
            'message': '请求参数错误',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='password-reset-confirm')
    def password_reset_confirm(self, request):
        """验证验证码并重置密码"""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            verification_code = serializer.validated_data['verification_code']
            new_password = serializer.validated_data['new_password']
            
            # 验证验证码（演示用，实际应该从缓存或数据库验证）
            if verification_code != "123456":  # 演示用验证码
                return Response({
                    'code': 400,
                    'message': '验证码错误'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 更新密码
            try:
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                
                return Response({
                    'code': 200,
                    'message': '密码重置成功'
                })
            except User.DoesNotExist:
                return Response({
                    'code': 400,
                    'message': '用户不存在'
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'code': 400,
            'message': '请求参数错误',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='delete-volunteer', permission_classes=[IsAdminUser])
    def delete_volunteer(self, request, pk=None):
        """
        管理员删除志愿者用户
        """
        try:
            user = self.get_object()
            if user.user_type == 'volunteer':
                username = user.username
                # 同时删除相关的志愿者档案
                try:
                    VolunteerProfile.objects.filter(user=user).delete()
                except Exception as e:
                    # 删除志愿者档案时出错的日志记录
                    pass
                
                user.delete()
                
                return Response({
                    'code': 200,
                    'message': f'志愿者用户 {username} 删除成功'
                })
            else:
                return Response({
                    'code': 400,
                    'message': '该用户不是志愿者类型'
                }, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({
                'code': 404,
                'message': '用户不存在'
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], url_path='password-change')
    def password_change(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']
            
            # 验证旧密码
            if not user.check_password(old_password):
                return Response({
                    'code': 400,
                    'message': '原密码错误'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 更新密码
            user.set_password(new_password)
            user.save()
            
            return Response({
                'code': 200,
                'message': '密码修改成功'
            })
        return Response({
            'code': 400,
            'message': '请求参数错误',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
