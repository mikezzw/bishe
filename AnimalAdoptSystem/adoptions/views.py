from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import AdoptionApplication, AdoptionMatch
from .serializers import AdoptionApplicationSerializer, AdoptionApplicationCreateSerializer, AdoptionApplicationUpdateSerializer, AdoptionMatchSerializer
from animals.models import Animal

class AdoptionApplicationViewSet(viewsets.ModelViewSet):
    queryset = AdoptionApplication.objects.all()
    serializer_class = AdoptionApplicationSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return AdoptionApplicationCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return AdoptionApplicationUpdateSerializer
        return AdoptionApplicationSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            application = serializer.save()
            return Response({
                'code': 200,
                'message': '申请提交成功',
                'data': AdoptionApplicationSerializer(application).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'code': 400,
            'message': '申请提交失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        application = self.get_object()
        serializer = self.get_serializer(application, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            # 如果审核通过，更新动物状态为已领养
            if application.status == 'approved':
                animal = application.animal
                animal.status = 'adopted'
                animal.save()
            return Response({
                'code': 200,
                'message': '审核成功',
                'data': AdoptionApplicationSerializer(application).data
            })
        return Response({
            'code': 400,
            'message': '审核失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='my-applications')
    def my_applications(self, request):
        applications = AdoptionApplication.objects.filter(applicant=request.user)
        serializer = AdoptionApplicationSerializer(applications, many=True)
        return Response({
            'code': 200,
            'message': '获取我的申请成功',
            'data': serializer.data
        })

    @action(detail=False, methods=['get'], url_path='pending')
    def pending_applications(self, request):
        applications = AdoptionApplication.objects.filter(status='pending')
        serializer = AdoptionApplicationSerializer(applications, many=True)
        return Response({
            'code': 200,
            'message': '获取待审核申请成功',
            'data': serializer.data
        })

class AdoptionMatchViewSet(viewsets.ModelViewSet):
    queryset = AdoptionMatch.objects.all()
    serializer_class = AdoptionMatchSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='calculate-match')
    def calculate_match(self, request):
        user = request.user
        user_scores = request.data.get('user_scores', {})
        animal_id = request.data.get('animal_id')
        
        # 验证用户输入
        required_traits = ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
        for trait in required_traits:
            if trait not in user_scores:
                return Response({
                    'code': 400,
                    'message': f'缺少{trait}评分'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 验证分数范围
            score = float(user_scores[trait])
            if not 1 <= score <= 5:
                return Response({
                    'code': 400,
                    'message': f'{trait}评分应在1-5之间'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 获取指定动物或所有可用动物
            if animal_id:
                animals = [Animal.objects.get(id=animal_id, status='available')]
            else:
                animals = Animal.objects.filter(status='available')
        except Animal.DoesNotExist:
            return Response({
                'code': 404,
                'message': '动物不存在或不可领养'
            }, status=status.HTTP_404_NOT_FOUND)
        
        matches = []
        
        for animal in animals:
            # 计算OCEAN性格匹配度
            match_score, match_details = self.calculate_ocean_compatibility(user_scores, animal)
            
            # 生成匹配理由
            match_reason = self.generate_match_reason(match_details, animal)
            
            # 保存匹配结果
            match = AdoptionMatch.objects.create(
                user=user,
                animal=animal,
                match_score=match_score,
                match_reason=match_reason
            )
            matches.append(match)
        
        # 按匹配分数排序
        matches.sort(key=lambda x: x.match_score, reverse=True)
        serializer = AdoptionMatchSerializer(matches[:10], many=True)
        
        return Response({
            'code': 200,
            'message': '匹配计算成功',
            'data': serializer.data
        })
    
    def calculate_ocean_compatibility(self, user_scores, animal):
        """
        基于OCEAN五大人格特质计算用户与动物的兼容性
        返回匹配分数(0-1)和详细信息
        """
        compatibility_factors = []
        details = {}
        
        # 宜人性 (Agreeableness) 匹配
        user_agreeableness = float(user_scores['agreeableness'])
        animal_agreeableness = animal.animal_agreeableness
        agreeableness_match = 1 - abs(user_agreeableness - animal_agreeableness) / 4
        compatibility_factors.append(agreeableness_match * 0.25)  # 权重25%
        details['agreeableness'] = {
            'user': user_agreeableness,
            'animal': animal_agreeableness,
            'match': agreeableness_match
        }
        
        # 外向性 (Extraversion) 匹配
        user_extraversion = float(user_scores['extraversion'])
        animal_extraversion = animal.animal_extraversion
        extraversion_match = 1 - abs(user_extraversion - animal_extraversion) / 4
        compatibility_factors.append(extraversion_match * 0.20)  # 权重20%
        details['extraversion'] = {
            'user': user_extraversion,
            'animal': animal_extraversion,
            'match': extraversion_match
        }
        
        # 尽责性 (Conscientiousness) 匹配
        user_conscientiousness = float(user_scores['conscientiousness'])
        animal_conscientiousness = animal.animal_conscientiousness
        conscientiousness_match = 1 - abs(user_conscientiousness - animal_conscientiousness) / 4
        compatibility_factors.append(conscientiousness_match * 0.20)  # 权重20%
        details['conscientiousness'] = {
            'user': user_conscientiousness,
            'animal': animal_conscientiousness,
            'match': conscientiousness_match
        }
        
        # 开放性 (Openness) 匹配
        user_openness = float(user_scores['openness'])
        animal_openness = animal.animal_openness
        openness_match = 1 - abs(user_openness - animal_openness) / 4
        compatibility_factors.append(openness_match * 0.20)  # 权重20%
        details['openness'] = {
            'user': user_openness,
            'animal': animal_openness,
            'match': openness_match
        }
        
        # 神经质 (Neuroticism) 负向匹配（越低越好）
        user_neuroticism = float(user_scores['neuroticism'])
        animal_neuroticism = animal.animal_neuroticism
        # 对于神经质，我们希望用户和动物都相对稳定
        neuroticism_stability = (5 - user_neuroticism) / 4  # 用户稳定性
        animal_stability = (5 - animal_neuroticism) / 4     # 动物稳定性
        neuroticism_match = min(neuroticism_stability, animal_stability)  # 取较小值
        compatibility_factors.append(neuroticism_match * 0.15)  # 权重15%
        details['neuroticism'] = {
            'user': user_neuroticism,
            'animal': animal_neuroticism,
            'user_stability': neuroticism_stability,
            'animal_stability': animal_stability,
            'match': neuroticism_match
        }
        
        # 计算总匹配度
        total_match = sum(compatibility_factors)
        
        return total_match, details
    
    def generate_match_reason(self, match_details, animal):
        """根据匹配详情生成匹配理由"""
        reasons = []
        
        # 分析各个维度的匹配情况
        if match_details['agreeableness']['match'] > 0.7:
            reasons.append(f"您和{animal.name}都很友善温和")
        elif match_details['agreeableness']['match'] < 0.3:
            reasons.append(f"您和{animal.name}的性格互补性强")
        
        if match_details['extraversion']['match'] > 0.7:
            reasons.append(f"您和{animal.name}都喜欢活跃的环境")
        elif match_details['extraversion']['match'] < 0.3:
            reasons.append(f"您和{animal.name}的能量水平形成良好平衡")
        
        if match_details['conscientiousness']['match'] > 0.7:
            reasons.append(f"您和{animal.name}都很有规律性")
        
        if match_details['openness']['match'] > 0.7:
            reasons.append(f"您和{animal.name}都对新事物保持开放态度")
        
        # 稳定性分析
        avg_stability = (match_details['neuroticism']['user_stability'] + 
                        match_details['neuroticism']['animal_stability']) / 2
        if avg_stability > 0.7:
            reasons.append("你们都能提供稳定的环境")
        
        # 如果没有特别的理由，给出通用建议
        if not reasons:
            reasons.append(f"根据综合性格分析，您与{animal.name}有良好的适配潜力")
            reasons.append("建议进一步了解彼此的生活习惯")
        
        return "；".join(reasons)
