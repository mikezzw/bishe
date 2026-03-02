from django.contrib import admin
from .models import Animal

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ['name', 'species', 'breed', 'age', 'gender', 'status', 'shelter', 'created_at']
    list_filter = ['species', 'status', 'gender', 'shelter']
    search_fields = ['name', 'breed', 'description']
    ordering = ['-created_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'species', 'breed', 'age', 'gender', 'weight')
        }),
        ('状态信息', {
            'fields': ('status', 'shelter')
        }),
        ('详细描述', {
            'fields': ('description', 'personality', 'health_status')
        }),
        ('媒体信息', {
            'fields': ('images',)
        }),
        ('发现信息', {
            'fields': ('found_place', 'found_date')
        }),
        ('性格特征', {
            'fields': ('animal_openness', 'animal_conscientiousness', 'animal_extraversion', 'animal_agreeableness', 'animal_neuroticism')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
