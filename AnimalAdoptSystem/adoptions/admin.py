from django.contrib import admin
from .models import AdoptionApplication, AdoptionMatch

@admin.register(AdoptionApplication)
class AdoptionApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'animal', 'status', 'contact_phone', 'created_at', 'reviewed_at']
    list_filter = ['status', 'created_at']
    search_fields = ['applicant__username', 'animal__name', 'application_reason']
    ordering = ['-created_at']
    
    fieldsets = (
        ('申请信息', {
            'fields': ('applicant', 'animal', 'status')
        }),
        ('申请详情', {
            'fields': ('application_reason', 'personal_info')
        }),
        ('联系方式', {
            'fields': ('contact_phone', 'contact_address')
        }),
        ('审核信息', {
            'fields': ('reviewer', 'review_comments', 'reviewed_at')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'reviewed_at']

@admin.register(AdoptionMatch)
class AdoptionMatchAdmin(admin.ModelAdmin):
    list_display = ['user', 'animal', 'match_score', 'created_at']
    list_filter = ['match_score', 'created_at']
    search_fields = ['user__username', 'animal__name', 'match_reason']
    ordering = ['-match_score', '-created_at']
    
    fieldsets = (
        ('匹配信息', {
            'fields': ('user', 'animal', 'match_score')
        }),
        ('匹配详情', {
            'fields': ('match_reason',)
        }),
        ('时间信息', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']
