from rest_framework import serializers
from .models import VolunteerProfile, VolunteerTask, VolunteerActivity, ActivityParticipant
from users.serializers import UserSerializer

class VolunteerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = VolunteerProfile
        fields = '__all__'

class VolunteerProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerProfile
        fields = ('name', 'gender', 'age', 'education', 'occupation', 'skills', 'availability', 'experience', 'motivation')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        profile = VolunteerProfile.objects.create(**validated_data)
        # 更新用户类型为志愿者
        profile.user.user_type = 'volunteer'
        profile.user.save()
        return profile

class VolunteerTaskSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = VolunteerTask
        fields = '__all__'

class VolunteerTaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerTask
        fields = ('title', 'description', 'location', 'start_time', 'end_time', 'required_skills')

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        task = VolunteerTask.objects.create(**validated_data)
        return task

class VolunteerTaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerTask
        fields = ('title', 'description', 'location', 'start_time', 'end_time', 'required_skills', 'status', 'assigned_to')

from shelters.serializers import ShelterSerializer

class VolunteerActivitySerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)
    participants = UserSerializer(read_only=True, many=True)
    shelter = ShelterSerializer(read_only=True)

    class Meta:
        model = VolunteerActivity
        fields = '__all__'

class VolunteerActivityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerActivity
        fields = ('name', 'description', 'location', 'start_time', 'end_time', 'capacity', 'shelter')

    def create(self, validated_data):
        validated_data['organizer'] = self.context['request'].user
        # 如果用户是基地管理员，自动设置shelter字段
        user = self.context['request'].user
        if hasattr(user, 'shelter'):
            validated_data['shelter'] = user.shelter
        activity = VolunteerActivity.objects.create(**validated_data)
        return activity

class VolunteerActivityUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerActivity
        fields = ('name', 'description', 'location', 'start_time', 'end_time', 'capacity', 'status')

class ActivityParticipantSerializer(serializers.ModelSerializer):
    activity = VolunteerActivitySerializer(read_only=True)
    participant = UserSerializer(read_only=True)

    class Meta:
        model = ActivityParticipant
        fields = '__all__'

class ActivityParticipantCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityParticipant
        fields = ('activity',)

    def create(self, validated_data):
        validated_data['participant'] = self.context['request'].user
        participant = ActivityParticipant.objects.create(**validated_data)
        return participant

class ActivityParticipantUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityParticipant
        fields = ('status',)
