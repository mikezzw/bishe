from rest_framework import serializers
from .models import Animal
from shelters.models import Shelter
# 延迟导入避免循环依赖
# from shelters.serializers import ShelterSerializer


class AnimalSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    shelter_info = serializers.SerializerMethodField()

    class Meta:
        model = Animal
        fields = '__all__'
        read_only_fields = ('animal_openness', 'animal_conscientiousness', 'animal_extraversion', 
                           'animal_agreeableness', 'animal_neuroticism')
    
    def get_images(self, obj):
        if obj.images and isinstance(obj.images, list):
            return obj.images
        return []
    
    def get_shelter_info(self, obj):
        if obj.shelter:
            return {
                'id': obj.shelter.id,
                'name': obj.shelter.name,
                'address': obj.shelter.address
            }
        return None

class AnimalCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animal
        fields = ('name', 'species', 'breed', 'age', 'gender', 'weight', 'description', 'personality', 'health_status', 'images', 'found_place', 'found_date', 'shelter')

class AnimalUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animal
        fields = ('name', 'species', 'breed', 'age', 'gender', 'weight', 'status', 'description', 'personality', 'health_status', 'images', 'found_place', 'found_date')
