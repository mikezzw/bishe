from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import VolunteerProfile, VolunteerTask, VolunteerActivity, ActivityParticipant
from .serializers import (
    VolunteerProfileSerializer, VolunteerProfileCreateSerializer,
    VolunteerTaskSerializer, VolunteerTaskCreateSerializer, VolunteerTaskUpdateSerializer,
    VolunteerActivitySerializer, VolunteerActivityCreateSerializer, VolunteerActivityUpdateSerializer,
    ActivityParticipantSerializer, ActivityParticipantCreateSerializer, ActivityParticipantUpdateSerializer
)

class VolunteerProfileViewSet(viewsets.ModelViewSet):
    queryset = VolunteerProfile.objects.all()
    serializer_class = VolunteerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return VolunteerProfileCreateSerializer
        return VolunteerProfileSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(user=self.request.user)

    def create(self, request):
        # 检查是否已有志愿者资料
        if VolunteerProfile.objects.filter(user=request.user).exists():
            return Response({
                'code': 400,
                'message': '您已经提交过志愿者申请'
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            profile = serializer.save()
            return Response({
                'code': 200,
                'message': '志愿者申请提交成功，等待审核',
                'data': VolunteerProfileSerializer(profile).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'code': 400,
            'message': '志愿者申请提交失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='approve')
    def approve_profile(self, request, pk=None):
        if not request.user.is_staff:
            return Response({
                'code': 403,
                'message': '只有管理员可以审核志愿者申请'
            }, status=status.HTTP_403_FORBIDDEN)
        profile = self.get_object()
        profile.status = 'approved'
        profile.save()
        return Response({
            'code': 200,
            'message': '志愿者申请审核通过',
            'data': VolunteerProfileSerializer(profile).data
        })

    @action(detail=True, methods=['post'], url_path='reject')
    def reject_profile(self, request, pk=None):
        if not request.user.is_staff:
            return Response({
                'code': 403,
                'message': '只有管理员可以审核志愿者申请'
            }, status=status.HTTP_403_FORBIDDEN)
        profile = self.get_object()
        profile.status = 'rejected'
        profile.save()
        return Response({
            'code': 200,
            'message': '志愿者申请审核拒绝',
            'data': VolunteerProfileSerializer(profile).data
        })

class VolunteerTaskViewSet(viewsets.ModelViewSet):
    queryset = VolunteerTask.objects.all()
    serializer_class = VolunteerTaskSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return VolunteerTaskCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return VolunteerTaskUpdateSerializer
        return VolunteerTaskSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            task = serializer.save()
            return Response({
                'code': 200,
                'message': '任务创建成功',
                'data': VolunteerTaskSerializer(task).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'code': 400,
            'message': '任务创建失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='assign')
    def assign_task(self, request, pk=None):
        task = self.get_object()
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({
                'code': 400,
                'message': '请指定分配对象'
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            from users.models import User
            user = User.objects.get(id=user_id)
            task.assigned_to = user
            task.status = 'assigned'
            task.save()
            return Response({
                'code': 200,
                'message': '任务分配成功',
                'data': VolunteerTaskSerializer(task).data
            })
        except User.DoesNotExist:
            return Response({
                'code': 404,
                'message': '用户不存在'
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='start')
    def start_task(self, request, pk=None):
        task = self.get_object()
        if task.assigned_to != request.user:
            return Response({
                'code': 403,
                'message': '只有任务负责人可以开始任务'
            }, status=status.HTTP_403_FORBIDDEN)
        task.status = 'in_progress'
        task.save()
        return Response({
            'code': 200,
            'message': '任务已开始',
            'data': VolunteerTaskSerializer(task).data
        })

    @action(detail=True, methods=['post'], url_path='complete')
    def complete_task(self, request, pk=None):
        task = self.get_object()
        if task.assigned_to != request.user:
            return Response({
                'code': 403,
                'message': '只有任务负责人可以完成任务'
            }, status=status.HTTP_403_FORBIDDEN)
        task.status = 'completed'
        task.save()
        return Response({
            'code': 200,
            'message': '任务已完成',
            'data': VolunteerTaskSerializer(task).data
        })

class VolunteerActivityViewSet(viewsets.ModelViewSet):
    queryset = VolunteerActivity.objects.all()
    serializer_class = VolunteerActivitySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return VolunteerActivityCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return VolunteerActivityUpdateSerializer
        return VolunteerActivitySerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            activity = serializer.save()
            return Response({
                'code': 200,
                'message': '活动创建成功',
                'data': VolunteerActivitySerializer(activity).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'code': 400,
            'message': '活动创建失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='register')
    def register_activity(self, request, pk=None):
        activity = self.get_object()
        # 检查是否已经报名
        if ActivityParticipant.objects.filter(activity=activity, participant=request.user).exists():
            return Response({
                'code': 400,
                'message': '您已经报名参加此活动'
            }, status=status.HTTP_400_BAD_REQUEST)
        # 检查活动是否已满
        if activity.participants.count() >= activity.capacity:
            return Response({
                'code': 400,
                'message': '活动人数已满'
            }, status=status.HTTP_400_BAD_REQUEST)
        # 检查活动状态
        if activity.status not in ['planning', 'upcoming']:
            return Response({
                'code': 400,
                'message': '活动已开始或已结束，无法报名'
            }, status=status.HTTP_400_BAD_REQUEST)
        # 创建报名记录
        participant = ActivityParticipant.objects.create(activity=activity, participant=request.user)
        return Response({
            'code': 200,
            'message': '报名成功',
            'data': ActivityParticipantSerializer(participant).data
        })

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_activity(self, request, pk=None):
        activity = self.get_object()
        try:
            participant = ActivityParticipant.objects.get(activity=activity, participant=request.user)
            participant.delete()
            return Response({
                'code': 200,
                'message': '取消报名成功'
            })
        except ActivityParticipant.DoesNotExist:
            return Response({
                'code': 404,
                'message': '您未报名参加此活动'
            }, status=status.HTTP_404_NOT_FOUND)

class ActivityParticipantViewSet(viewsets.ModelViewSet):
    queryset = ActivityParticipant.objects.all()
    serializer_class = ActivityParticipantSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(participant=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return ActivityParticipantCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ActivityParticipantUpdateSerializer
        return ActivityParticipantSerializer

    @action(detail=False, methods=['get'], url_path='my-participations')
    def my_participations(self, request):
        participations = self.get_queryset()
        serializer = ActivityParticipantSerializer(participations, many=True)
        return Response({
            'code': 200,
            'message': '获取我的活动参与记录成功',
            'data': serializer.data
        })
