from rest_framework import serializers
from django.utils import timezone
import base64
from .models import Shelter, ShelterStaff, Donation, InteractionApplication, ShelterActivity, DonationUsage
# 延迟导入避免循环依赖
# from users.serializers import UserSerializer
# from animals.serializers import AnimalSerializer

class ShelterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shelter
        fields = '__all__'
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # 处理 JSONField 格式的 qr_code
        if instance.qr_code and isinstance(instance.qr_code, list) and len(instance.qr_code) > 0:
            # 返回数组中的第一个 Base64 字符串
            representation['qr_code'] = instance.qr_code[0]
        else:
            representation['qr_code'] = None
        return representation

class ShelterCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shelter
        fields = ['name', 'description', 'address', 'contact_name', 'contact_phone', 'email', 'website', 'capacity', 'qr_code']

class ShelterUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shelter
        fields = ['name', 'description', 'address', 'contact_name', 'contact_phone', 'email', 'website', 'capacity', 'qr_code', 'status']

class ShelterStaffSerializer(serializers.ModelSerializer):
    shelter = ShelterSerializer(read_only=True)
    user = serializers.SerializerMethodField()
    
    def get_user(self, obj):
        from users.serializers import UserSerializer
        return UserSerializer(obj.user).data
    
    class Meta:
        model = ShelterStaff
        fields = '__all__'

class ShelterStaffCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShelterStaff
        fields = ['shelter', 'user', 'role']

class DonationSerializer(serializers.ModelSerializer):
    shelter = ShelterSerializer(read_only=True)
    donor = serializers.SerializerMethodField()
    
    def get_donor(self, obj):
        if obj.donor:
            from users.serializers import UserSerializer
            return UserSerializer(obj.donor).data
        return None
    
    class Meta:
        model = Donation
        fields = '__all__'
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # 确保donor为None时不会导致错误
        if not instance.donor:
            representation['donor'] = None
        return representation

class DonationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = ('donor_name', 'amount', 'goods_description', 'service_description', 'donation_type')
    
    def validate(self, data):
        donation_type = data.get('donation_type')
        if donation_type == 'money' and not data.get('amount'):
            raise serializers.ValidationError('金钱捐赠必须填写金额')
        elif donation_type == 'goods' and not data.get('goods_description'):
            raise serializers.ValidationError('物品捐赠必须填写物品描述')
        elif donation_type == 'service' and not data.get('service_description'):
            raise serializers.ValidationError('服务捐赠必须填写服务描述')
        return data
    
    def create(self, validated_data):
        # 只有当没有提供donor_name时，才使用当前用户作为捐赠人
        if not validated_data.get('donor_name'):
            validated_data['donor'] = self.context['request'].user
        return super().create(validated_data)

class DonationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = ('status', 'review_comments')

class InteractionApplicationSerializer(serializers.ModelSerializer):
    shelter = ShelterSerializer(read_only=True)
    applicant = serializers.SerializerMethodField()
    # animal = AnimalSerializer(read_only=True)  # 避免循环导入
    reviewer = serializers.SerializerMethodField()
    
    def get_applicant(self, obj):
        from users.serializers import UserSerializer
        return UserSerializer(obj.applicant).data
    
    def get_reviewer(self, obj):
        if obj.reviewer:
            from users.serializers import UserSerializer
            return UserSerializer(obj.reviewer).data
        return None
    
    class Meta:
        model = InteractionApplication
        fields = '__all__'

class InteractionApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InteractionApplication
        fields = ('shelter', 'animal', 'application_type', 'purpose', 'desired_date')
    
    def create(self, validated_data):
        validated_data['applicant'] = self.context['request'].user
        return super().create(validated_data)

class ShelterActivitySerializer(serializers.ModelSerializer):
    shelter = ShelterSerializer(read_only=True)
    created_by = serializers.SerializerMethodField()
    
    def get_created_by(self, obj):
        from users.serializers import UserSerializer
        return UserSerializer(obj.created_by).data
    
    class Meta:
        model = ShelterActivity
        fields = '__all__'

class ShelterActivityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShelterActivity
        fields = ('title', 'description', 'activity_type', 'location', 'start_time', 'end_time', 'capacity')
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        # shelter会在ViewSet中设置
        return super().create(validated_data)

class ShelterActivityUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShelterActivity
        fields = ['title', 'description', 'activity_type', 'location', 'start_time', 'end_time', 'capacity', 'status']

class InteractionApplicationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InteractionApplication
        fields = ('status', 'review_comments')

    def update(self, instance, validated_data):
        if 'status' in validated_data and validated_data['status'] in ['approved', 'rejected']:
            validated_data['reviewer'] = self.context['request'].user
            validated_data['reviewed_at'] = timezone.now()
        return super().update(instance, validated_data)


class DonationUsageSerializer(serializers.ModelSerializer):
    donation = DonationSerializer(read_only=True)
    approver = serializers.CharField(source='approver.username', read_only=True, allow_null=True)
    
    class Meta:
        model = DonationUsage
        fields = '__all__'


class DonationUsageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonationUsage
        fields = ('donation', 'amount', 'usage_type', 'purpose', 'description', 'attachments', 'usage_date')
    
    def validate(self, data):
        # 验证使用金额不超过捐赠金额
        donation = data.get('donation')
        amount = data.get('amount')
        
        if donation and donation.donation_type == 'money' and amount:
            total_used = sum(usage.amount for usage in donation.usages.all())
            if total_used + amount > (donation.amount or 0):
                raise serializers.ValidationError('使用金额不能超过捐赠金额')
        
        return data
    
    def create(self, validated_data):
        validated_data['approver'] = self.context['request'].user
        return super().create(validated_data)


class DonationUsageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonationUsage
        fields = ('amount', 'usage_type', 'purpose', 'description', 'attachments', 'usage_date')
    
    def validate(self, data):
        instance = self.instance
        if instance and 'amount' in data:
            # 验证更新后的金额
            donation = instance.donation
            if donation.donation_type == 'money':
                total_used = sum(usage.amount for usage in donation.usages.exclude(pk=instance.pk))
                if total_used + data['amount'] > (donation.amount or 0):
                    raise serializers.ValidationError('使用金额不能超过捐赠金额')
        return data
