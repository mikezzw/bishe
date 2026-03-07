from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from .models import Shelter, ShelterStaff, Donation, InteractionApplication, ShelterActivity, DonationUsage
from .serializers import (
    ShelterSerializer, ShelterCreateSerializer, ShelterUpdateSerializer,
    ShelterStaffSerializer, ShelterStaffCreateSerializer,
    DonationSerializer, DonationCreateSerializer, DonationUpdateSerializer,
    InteractionApplicationSerializer, InteractionApplicationCreateSerializer, InteractionApplicationUpdateSerializer,
    ShelterActivitySerializer, ShelterActivityCreateSerializer, ShelterActivityUpdateSerializer,
    DonationUsageSerializer, DonationUsageCreateSerializer, DonationUsageUpdateSerializer
)

class ShelterViewSet(viewsets.ModelViewSet):
    queryset = Shelter.objects.all()
    serializer_class = ShelterSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'get_donations_statistics']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return ShelterCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ShelterUpdateSerializer
        return ShelterSerializer

    def list(self, request):
        # 获取查询集
        queryset = self.get_queryset()
        
        # 应用过滤
        queryset = self.filter_queryset(queryset)
        
        # 分页处理
        page = self.paginate_queryset(queryset)
        if page is not None:
            # 手动序列化数据
            serialized_data = []
            for shelter in page:
                shelter_data = {
                    'id': shelter.id,
                    'name': shelter.name,
                    'description': shelter.description,
                    'address': shelter.address,
                    'contact_name': shelter.contact_name,
                    'contact_phone': shelter.contact_phone,
                    'email': shelter.email,
                    'website': shelter.website,
                    'capacity': shelter.capacity,
                    'current_animals': shelter.current_animals,
                    'status': shelter.status,
                    'created_at': shelter.created_at,
                    'updated_at': shelter.updated_at,
                    'qr_code': shelter.qr_code or None  # JSONField 直接返回
                }
                serialized_data.append(shelter_data)
            
            # 构建分页响应
            pagination_data = {
                'count': self.get_queryset().count(),
                'next': self.paginator.get_next_link(),
                'previous': self.paginator.get_previous_link(),
                'results': serialized_data
            }
            
            # 构建最终响应格式
            response_data = {
                'code': 200,
                'message': '获取基地列表成功',
                'data': pagination_data
            }
            return Response(response_data)
        
        # 非分页处理
        shelters = queryset
        serialized_data = []
        for shelter in shelters:
            shelter_data = {
                'id': shelter.id,
                'name': shelter.name,
                'description': shelter.description,
                'address': shelter.address,
                'contact_name': shelter.contact_name,
                'contact_phone': shelter.contact_phone,
                'email': shelter.email,
                'website': shelter.website,
                'capacity': shelter.capacity,
                'current_animals': shelter.current_animals,
                'status': shelter.status,
                'created_at': shelter.created_at,
                'updated_at': shelter.updated_at,
                'qr_code': shelter.qr_code or None  # JSONField 直接返回
            }
            serialized_data.append(shelter_data)
        return Response({
            'code': 200,
            'message': '获取基地列表成功',
            'data': serialized_data
        })

    def retrieve(self, request, pk=None):
        shelter = self.get_object()
        # 手动序列化数据
        shelter_data = {
            'id': shelter.id,
            'name': shelter.name,
            'description': shelter.description,
            'address': shelter.address,
            'contact_name': shelter.contact_name,
            'contact_phone': shelter.contact_phone,
            'email': shelter.email,
            'website': shelter.website,
            'capacity': shelter.capacity,
            'current_animals': shelter.current_animals,
            'status': shelter.status,
            'created_at': shelter.created_at,
            'updated_at': shelter.updated_at,
            'qr_code': shelter.qr_code or None  # JSONField 直接返回
        }
        return Response({
            'code': 200,
            'message': '获取基地详情成功',
            'data': shelter_data
        })
        
    @action(detail=True, methods=['get'], url_path='donations-statistics')
    def get_donations_statistics(self, request, pk=None):
        """获取基地的捐赠和使用统计信息"""
        from django.db.models import Sum, Count
        shelter = self.get_object()
            
        # 获取所有捐赠
        donations = Donation.objects.filter(shelter=shelter)
            
        # 计算捐赠总额
        total_donations_amount = donations.aggregate(total=Sum('amount'))['total'] or 0
            
        # 获取所有捐赠使用记录
        donation_ids = list(donations.values_list('id', flat=True))
        usages = DonationUsage.objects.filter(donation_id__in=donation_ids)
            
        # 计算使用总额
        total_used_amount = usages.aggregate(total=Sum('amount'))['total'] or 0
            
        # 按用途类型统计
        usage_types_breakdown = dict(
            usages.values('usage_type').annotate(count=Count('usage_type')).values_list('usage_type', 'count')
        )
            
        # 最近的使用记录
        recent_usages = DonationUsageSerializer(usages.order_by('-created_at')[:5], many=True).data
            
        stats = {
            'total_donations_amount': float(total_donations_amount),
            'total_used_amount': float(total_used_amount),
            'remaining_amount': float(total_donations_amount - total_used_amount),
            'total_donations_count': donations.count(),
            'total_usages_count': usages.count(),
            'usage_types_breakdown': usage_types_breakdown,
            'recent_usages': recent_usages
        }
            
        return Response({
            'code': 200,
            'message': '获取捐赠统计信息成功',
            'data': stats
        })

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            shelter = serializer.save()
            # 创建者自动成为管理员
            ShelterStaff.objects.create(
                shelter=shelter,
                user=request.user,
                role='manager'
            )
            # 手动序列化数据
            shelter_data = {
                'id': shelter.id,
                'name': shelter.name,
                'description': shelter.description,
                'address': shelter.address,
                'contact_name': shelter.contact_name,
                'contact_phone': shelter.contact_phone,
                'email': shelter.email,
                'website': shelter.website,
                'capacity': shelter.capacity,
                'current_animals': shelter.current_animals,
                'status': shelter.status,
                'created_at': shelter.created_at,
                'updated_at': shelter.updated_at,
                'qr_code': shelter.qr_code or None  # JSONField 直接返回
            }
            return Response({
                'code': 200,
                'message': '动物基地创建成功',
                'data': shelter_data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'code': 400,
            'message': '动物基地创建失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='staff')
    def get_staff(self, request, pk=None):
        shelter = self.get_object()
        staff = shelter.staff.all()
        serializer = ShelterStaffSerializer(staff, many=True)
        return Response({
            'code': 200,
            'message': '获取基地工作人员成功',
            'data': serializer.data
        })

    def destroy(self, request, pk=None):
        """删除基地及其关联数据"""
        shelter = self.get_object()
        
        # 检查权限：只有超级管理员可以删除基地
        if not request.user.is_staff:
            return Response({
                'code': 403,
                'message': '只有系统管理员可以删除基地'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 统计关联数据
        from django.db.models import Count
        stats = {
            'staff_count': shelter.staff.count(),
            'activities_count': shelter.activities.count(),
            'donations_count': shelter.donations.count(),
            'interaction_applications_count': shelter.interaction_applications.count()
        }
        
        # 计算捐赠使用记录数量
        donation_ids = list(shelter.donations.values_list('id', flat=True))
        from .models import DonationUsage
        usages_count = DonationUsage.objects.filter(donation_id__in=donation_ids).count()
        stats['donation_usages_count'] = usages_count
        
        # 执行删除 (CASCADE 会自动删除关联数据)
        shelter_name = shelter.name
        shelter.delete()
        
        return Response({
            'code': 200,
            'message': f'基地 "{shelter_name}" 及其关联数据已删除',
            'deleted_stats': stats
        }, status=status.HTTP_204_NO_CONTENT)

class ShelterStaffViewSet(viewsets.ModelViewSet):
    queryset = ShelterStaff.objects.all()
    serializer_class = ShelterStaffSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return ShelterStaffCreateSerializer
        return ShelterStaffSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # 检查是否已经是该基地的工作人员
            shelter = serializer.validated_data['shelter']
            user = serializer.validated_data['user']
            if ShelterStaff.objects.filter(shelter=shelter, user=user).exists():
                return Response({
                    'code': 400,
                    'message': '该用户已经是该基地的工作人员'
                }, status=status.HTTP_400_BAD_REQUEST)
            # 检查当前用户是否有权限添加工作人员
            if not ShelterStaff.objects.filter(shelter=shelter, user=request.user, role='manager').exists() and not request.user.is_staff:
                return Response({
                    'code': 403,
                    'message': '只有基地管理员可以添加工作人员'
                }, status=status.HTTP_403_FORBIDDEN)
            staff = serializer.save()
            return Response({
                'code': 200,
                'message': '工作人员添加成功',
                'data': ShelterStaffSerializer(staff).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'code': 400,
            'message': '工作人员添加失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        staff = self.get_object()
        # 检查当前用户是否有权限删除工作人员
        if not ShelterStaff.objects.filter(shelter=staff.shelter, user=request.user, role='manager').exists() and not request.user.is_staff:
            return Response({
                'code': 403,
                'message': '只有基地管理员可以删除工作人员'
            }, status=status.HTTP_403_FORBIDDEN)
        # 不能删除自己
        if staff.user == request.user:
            return Response({
                'code': 400,
                'message': '不能删除自己'
            }, status=status.HTTP_400_BAD_REQUEST)
        staff.delete()
        return Response({
            'code': 200,
            'message': '工作人员删除成功'
        }, status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>\d+)/shelter')
    def get_user_shelter(self, request, user_id=None):
        """获取用户所属的基地信息"""
        try:
            # 获取用户的所有基地记录
            staff_records = ShelterStaff.objects.filter(user_id=user_id)
            shelters = []
            
            # 如果有ShelterStaff记录，添加到列表中
            for record in staff_records:
                shelters.append({
                    'shelter': ShelterSerializer(record.shelter).data,
                    'role': record.role
                })
            
            # 如果没有ShelterStaff记录，检查User模型中的shelter字段
            if not shelters:
                from users.models import User
                try:
                    user = User.objects.get(id=user_id)
                    if user.shelter:
                        shelters.append({
                            'shelter': ShelterSerializer(user.shelter).data,
                            'role': 'manager'  # 默认角色为管理员
                        })
                except User.DoesNotExist:
                    pass
            
            if not shelters:
                return Response({
                    'code': 404,
                    'message': '用户未关联任何基地'
                }, status=status.HTTP_404_NOT_FOUND)
            
            return Response({
                'code': 200,
                'message': '获取用户基地信息成功',
                'data': shelters
            })
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取用户基地信息失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return DonationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return DonationUpdateSerializer
        return DonationSerializer

    def get_queryset(self):
        # 获取shelter_pk参数
        shelter_pk = self.kwargs.get('shelter_pk')
        if shelter_pk:
            return self.queryset.filter(shelter_id=shelter_pk)
        if self.request.user.is_staff:
            return self.queryset
        # 普通用户只能查看自己的捐赠记录
        return self.queryset.filter(donor=self.request.user)

    def list(self, request, shelter_pk=None):
        # 分页处理
        page = self.paginate_queryset(self.get_queryset())
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # 构建分页响应数据
            paginated_response = self.get_paginated_response(serializer.data)
            # 构建最终响应格式
            response_data = {
                'code': 200,
                'message': '获取捐赠记录成功',
                'data': paginated_response.data
            }
            return Response(response_data)
        
        # 非分页处理
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response({
            'code': 200,
            'message': '获取捐赠记录成功',
            'data': serializer.data
        })

    def create(self, request, shelter_pk=None):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # 设置shelter
            if shelter_pk:
                # 直接设置shelter字段，而不是shelter_id
                from .models import Shelter
                try:
                    shelter = Shelter.objects.get(pk=shelter_pk)
                    serializer.validated_data['shelter'] = shelter
                except Shelter.DoesNotExist:
                    return Response({
                        'code': 404,
                        'message': '基地不存在'
                    }, status=status.HTTP_404_NOT_FOUND)
            donation = serializer.save()
            return Response({
                'code': 200,
                'message': '捐赠提交成功',
                'data': DonationSerializer(donation).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'code': 400,
            'message': '捐赠提交失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        donation = self.get_object()
        # 检查当前用户是否有权限更新捐赠记录
        if not ShelterStaff.objects.filter(shelter=donation.shelter, user=request.user).exists() and not request.user.is_staff:
            return Response({
                'code': 403,
                'message': '只有基地工作人员可以更新捐赠记录'
            }, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(donation, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'code': 200,
                'message': '捐赠记录更新成功',
                'data': DonationSerializer(donation).data
            })
        return Response({
            'code': 400,
            'message': '捐赠记录更新失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class InteractionApplicationViewSet(viewsets.ModelViewSet):
    queryset = InteractionApplication.objects.all()
    serializer_class = InteractionApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return InteractionApplicationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return InteractionApplicationUpdateSerializer
        return InteractionApplicationSerializer

    def get_queryset(self):
        # 从URL参数中获取基地ID
        shelter_pk = self.kwargs.get('shelter_pk')
        if shelter_pk:
            # 如果提供了基地ID，只返回该基地的申请
            return self.queryset.filter(shelter_id=shelter_pk)
        
        if self.request.user.is_staff:
            return self.queryset
        # 普通用户只能查看自己的申请记录
        return self.queryset.filter(applicant=self.request.user)

    def list(self, request, shelter_pk=None):
        # 分页处理
        page = self.paginate_queryset(self.get_queryset())
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # 构建分页响应数据
            paginated_response = self.get_paginated_response(serializer.data)
            # 构建最终响应格式
            response_data = {
                'code': 200,
                'message': '获取互动申请列表成功',
                'data': paginated_response.data
            }
            return Response(response_data)
        
        # 非分页处理
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response({
            'code': 200,
            'message': '获取互动申请列表成功',
            'data': serializer.data
        })

    def create(self, request, shelter_pk=None):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # 设置 shelter（从 URL 参数获取）
            if shelter_pk:
                from .models import Shelter
                try:
                    shelter = Shelter.objects.get(pk=shelter_pk)
                    serializer.validated_data['shelter'] = shelter
                except Shelter.DoesNotExist:
                    return Response({
                        'code': 404,
                        'message': '基地不存在'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # animal 是可选的，如果前端传递了 activity 字段，忽略它
            # 因为 InteractionApplication 不需要 activity 字段
            if 'activity' in serializer.validated_data:
                del serializer.validated_data['activity']
            
            application = serializer.save()
            return Response({
                'code': 200,
                'message': '互动申请提交成功，等待审核',
                'data': InteractionApplicationSerializer(application).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'code': 400,
            'message': '互动申请提交失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        application = self.get_object()
        # 检查当前用户是否有权限更新申请记录
        if not ShelterStaff.objects.filter(shelter=application.shelter, user=request.user).exists() and not request.user.is_staff:
            return Response({
                'code': 403,
                'message': '只有基地工作人员可以更新申请记录'
            }, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(application, data=request.data, partial=True, context={'request': request, 'now': timezone.now()})
        if serializer.is_valid():
            application = serializer.save()
            return Response({
                'code': 200,
                'message': '互动申请更新成功',
                'data': InteractionApplicationSerializer(application).data
            })
        return Response({
            'code': 400,
            'message': '互动申请更新失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='approve')
    def approve_application(self, request, shelter_pk=None, pk=None):
        application = self.get_object()
        # 检查当前用户是否有权限审核申请
        is_staff = ShelterStaff.objects.filter(shelter=application.shelter, user=request.user).exists()
        is_admin = getattr(request.user, "shelter_id", None) == application.shelter.id
        is_superuser = request.user.is_staff
        
        if not (is_staff or is_admin or is_superuser):
            return Response({
                'code': 403,
                'message': '只有基地工作人员可以审核申请'
            }, status=status.HTTP_403_FORBIDDEN)
        application.status = 'approved'
        application.reviewer = request.user
        application.reviewed_at = timezone.now()
        application.review_comments = request.data.get('review_comments', '')
        application.save()
        return Response({
            'code': 200,
            'message': '互动申请审核通过',
            'data': InteractionApplicationSerializer(application).data
        })

    @action(detail=True, methods=['post'], url_path='reject')
    def reject_application(self, request, shelter_pk=None, pk=None):
        application = self.get_object()
        # 检查当前用户是否有权限审核申请
        is_staff = ShelterStaff.objects.filter(shelter=application.shelter, user=request.user).exists()
        is_admin = getattr(request.user, "shelter_id", None) == application.shelter.id
        is_superuser = request.user.is_staff
        
        if not (is_staff or is_admin or is_superuser):
            return Response({
                'code': 403,
                'message': '只有基地工作人员可以审核申请'
            }, status=status.HTTP_403_FORBIDDEN)
        application.status = 'rejected'
        application.reviewer = request.user
        application.reviewed_at = timezone.now()
        application.review_comments = request.data.get('review_comments', '')
        application.save()
        return Response({
            'code': 200,
            'message': '互动申请审核拒绝',
            'data': InteractionApplicationSerializer(application).data
        })

    @action(detail=True, methods=['post'], url_path='complete')
    def complete_application(self, request, shelter_pk=None, pk=None):
        application = self.get_object()
        # 检查当前用户是否有权限完成申请
        is_staff = ShelterStaff.objects.filter(shelter=application.shelter, user=request.user).exists()
        is_admin = getattr(request.user, "shelter_id", None) == application.shelter.id
        is_superuser = request.user.is_staff
        
        if not (is_staff or is_admin or is_superuser):
            return Response({
                'code': 403,
                'message': '只有基地工作人员可以完成申请'
            }, status=status.HTTP_403_FORBIDDEN)
        if application.status != 'approved':
            return Response({
                'code': 400,
                'message': '只有已通过的申请才能标记为完成'
            }, status=status.HTTP_400_BAD_REQUEST)
        application.status = 'completed'
        application.save()
        return Response({
            'code': 200,
            'message': '互动申请已完成',
            'data': InteractionApplicationSerializer(application).data
        })

class ShelterActivityViewSet(viewsets.ModelViewSet):
    queryset = ShelterActivity.objects.all()
    serializer_class = ShelterActivitySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return ShelterActivityCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ShelterActivityUpdateSerializer
        return ShelterActivitySerializer

    def get_queryset(self):
        # 获取shelter_pk参数
        shelter_pk = self.kwargs.get('shelter_pk')
        if shelter_pk:
            return self.queryset.filter(shelter_id=shelter_pk)
        return self.queryset

    def list(self, request, shelter_pk=None):
        # 分页处理
        page = self.paginate_queryset(self.get_queryset())
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # 构建分页响应数据
            paginated_response = self.get_paginated_response(serializer.data)
            # 构建最终响应格式
            response_data = {
                'code': 200,
                'message': '获取活动列表成功',
                'data': paginated_response.data
            }
            return Response(response_data)
        
        # 非分页处理
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response({
            'code': 200,
            'message': '获取活动列表成功',
            'data': serializer.data
        })

    def create(self, request, shelter_pk=None):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # 设置shelter
            serializer.validated_data['shelter_id'] = shelter_pk
            activity = serializer.save()
            return Response({
                'code': 200,
                'message': '活动创建成功',
                'data': ShelterActivitySerializer(activity).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'code': 400,
            'message': '活动创建失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        activity = self.get_object()
        # 检查当前用户是否有权限更新活动
        if not ShelterStaff.objects.filter(shelter=activity.shelter, user=request.user).exists() and not request.user.is_staff:
            return Response({
                'code': 403,
                'message': '只有基地工作人员可以更新活动'
            }, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(activity, data=request.data, partial=True)
        if serializer.is_valid():
            activity = serializer.save()
            return Response({
                'code': 200,
                'message': '活动更新成功',
                'data': ShelterActivitySerializer(activity).data
            })
        return Response({
            'code': 400,
            'message': '活动更新失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        activity = self.get_object()
        # 检查当前用户是否有权限删除活动
        if not ShelterStaff.objects.filter(shelter=activity.shelter, user=request.user).exists() and not request.user.is_staff:
            return Response({
                'code': 403,
                'message': '只有基地工作人员可以删除活动'
            }, status=status.HTTP_403_FORBIDDEN)
        activity.delete()
        return Response({
            'code': 200,
            'message': '活动删除成功'
        }, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='shelter/(?P<shelter_id>\d+)')
    def get_shelter_activities(self, request, shelter_id=None):
        activities = ShelterActivity.objects.filter(shelter_id=shelter_id)
        serializer = ShelterActivitySerializer(activities, many=True)
        return Response({
            'code': 200,
            'message': '获取基地活动成功',
            'data': serializer.data
        })

    @action(detail=True, methods=['post'], url_path='register')
    def register_activity(self, request, shelter_pk=None, pk=None):
        activity = self.get_object()
        # 检查是否已经报名（使用 purpose 字段存储活动ID）
        if InteractionApplication.objects.filter(
            applicant=request.user,
            shelter=activity.shelter,
            application_type='volunteer',
            purpose=f'activity_{activity.id}'
        ).exists():
            return Response({
                'code': 400,
                'message': '您已经报名参加此活动'
            }, status=status.HTTP_400_BAD_REQUEST)
        # 检查活动是否已满
        # 计算当前报名人数
        registration_count = InteractionApplication.objects.filter(
            shelter=activity.shelter,
            application_type='volunteer',
            purpose=f'activity_{activity.id}'
        ).count()
        if registration_count >= activity.capacity:
            return Response({
                'code': 400,
                'message': '活动人数已满'
            }, status=status.HTTP_400_BAD_REQUEST)
        # 检查活动状态
        if activity.status not in ['upcoming']:
            return Response({
                'code': 400,
                'message': '活动已开始或已结束，无法报名'
            }, status=status.HTTP_400_BAD_REQUEST)
        # 创建报名记录
        application = InteractionApplication.objects.create(
            applicant=request.user,
            shelter=activity.shelter,
            application_type='volunteer',
            purpose=f'activity_{activity.id}',
            desired_date=activity.start_time
        )
        return Response({
            'code': 200,
            'message': '报名成功',
            'data': InteractionApplicationSerializer(application).data
        })


class DonationUsageViewSet(viewsets.ModelViewSet):
    queryset = DonationUsage.objects.all()
    serializer_class = DonationUsageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DonationUsageCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return DonationUsageUpdateSerializer
        return DonationUsageSerializer
    
    def list(self, request, shelter_pk=None):
        # 分页处理
        page = self.paginate_queryset(self.get_queryset())
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # 构建分页响应数据
            paginated_response = self.get_paginated_response(serializer.data)
            # 构建最终响应格式
            response_data = {
                'code': 200,
                'message': '获取捐赠使用记录成功',
                'data': paginated_response.data
            }
            return Response(response_data)
        
        # 非分页处理
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response({
            'code': 200,
            'message': '获取捐赠使用记录成功',
            'data': serializer.data
        })
    
    def get_queryset(self):
        user = self.request.user
        # 管理员可以看到所有记录
        if user.is_staff:
            return self.queryset
        
        # 普通用户只能查看自己基地的使用记录
        try:
            # 先尝试从ShelterStaff表中获取用户的基地记录
            staff_record = ShelterStaff.objects.get(user=user)
            shelter_donations = Donation.objects.filter(shelter=staff_record.shelter)
            return self.queryset.filter(donation__in=shelter_donations)
        except ShelterStaff.DoesNotExist:
            # 如果ShelterStaff表中没有记录，尝试从用户的shelter字段中获取基地
            if user.shelter:
                shelter_donations = Donation.objects.filter(shelter=user.shelter)
                return self.queryset.filter(donation__in=shelter_donations)
            return self.queryset.none()
    
    def create(self, request, shelter_pk=None):
        serializer = self.get_serializer(data=request.data, context={'request': request, 'shelter_pk': shelter_pk})
        if serializer.is_valid():
            try:
                usage = serializer.save()
                return Response({
                    'code': 200,
                    'message': '捐赠使用记录创建成功',
                    'data': DonationUsageSerializer(usage).data
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'code': 400,
                    'message': f'创建失败: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'code': 400,
            'message': '捐赠使用记录创建失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, pk=None):
        usage = self.get_object()
        # 检查权限
        if not self._check_permission(request.user, usage.donation.shelter):
            return Response({
                'code': 403,
                'message': '没有权限更新此使用记录'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(usage, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                usage = serializer.save()
                return Response({
                    'code': 200,
                    'message': '捐赠使用记录更新成功',
                    'data': DonationUsageSerializer(usage).data
                })
            except Exception as e:
                return Response({
                    'code': 400,
                    'message': f'更新失败: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'code': 400,
            'message': '捐赠使用记录更新失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def _check_permission(self, user, shelter):
        """检查用户是否有权限操作指定基地的数据"""
        if user.is_staff:
            return True
        return ShelterStaff.objects.filter(shelter=shelter, user=user).exists()
    
    @action(detail=False, methods=['get'], url_path='donation/(?P<donation_id>\d+)')
    def get_donation_usages(self, request, donation_id=None):
        """获取特定捐赠的所有使用记录"""
        usages = self.queryset.filter(donation_id=donation_id)
        serializer = DonationUsageSerializer(usages, many=True)
        return Response({
            'code': 200,
            'message': '获取捐赠使用记录成功',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='statistics')
    def get_statistics(self, request):
        """获取捐赠使用统计信息"""
        from django.db.models import Sum, Count
        
        queryset = self.get_queryset()
        
        stats = {
            'total_usages': queryset.count(),
            'total_amount': queryset.aggregate(total=Sum('amount'))['total'] or 0,
            'usage_types_breakdown': dict(
                queryset.values('usage_type').annotate(count=Count('usage_type')).values_list('usage_type', 'count')
            ),
            'recent_usages': DonationUsageSerializer(queryset.order_by('-created_at')[:10], many=True).data
        }
        
        return Response({
            'code': 200,
            'message': '获取统计信息成功',
            'data': stats
        })
