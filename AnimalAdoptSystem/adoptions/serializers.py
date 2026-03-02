from rest_framework import serializers
from datetime import datetime
from .models import AdoptionApplication, AdoptionMatch
from users.serializers import UserSerializer
from animals.serializers import AnimalSerializer

class AdoptionApplicationSerializer(serializers.ModelSerializer):
    applicant = UserSerializer(read_only=True)
    animal = AnimalSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)

    class Meta:
        model = AdoptionApplication
        fields = '__all__'

class AdoptionApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdoptionApplication
        fields = ('animal', 'application_reason', 'personal_info', 'contact_phone', 'contact_address')

    def create(self, validated_data):
        validated_data['applicant'] = self.context['request'].user
        application = AdoptionApplication.objects.create(**validated_data)
        return application

class AdoptionApplicationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdoptionApplication
        fields = ('status', 'review_comments')

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.review_comments = validated_data.get('review_comments', instance.review_comments)
        instance.reviewer = self.context['request'].user
        instance.reviewed_at = datetime.now()
        instance.save()
        return instance

class AdoptionMatchSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    animal = AnimalSerializer(read_only=True)

    class Meta:
        model = AdoptionMatch
        fields = '__all__'
        read_only_fields = ('user', 'animal', 'match_score', 'match_reason', 'created_at')
