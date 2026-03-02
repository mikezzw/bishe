from django.contrib import admin
from .models import Shelter, ShelterActivity, ShelterStaff, Donation, InteractionApplication

@admin.register(Shelter)
class ShelterAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_name', 'contact_phone', 'email', 'status', 'current_animals', 'capacity', 'created_at']
    list_filter = ['status']
    search_fields = ['name', 'contact_name', 'email', 'address']
    ordering = ['-created_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description', 'address')
        }),
        ('联系方式', {
            'fields': ('contact_name', 'contact_phone', 'email', 'website')
        }),
        ('容量信息', {
            'fields': ('capacity', 'current_animals')
        }),
        ('状态设置', {
            'fields': ('status',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'current_animals']

@admin.register(ShelterActivity)
class ShelterActivityAdmin(admin.ModelAdmin):
    list_display = ['title', 'shelter', 'activity_type', 'status', 'start_time', 'capacity']
    list_filter = ['activity_type', 'status', 'shelter']
    search_fields = ['title', 'description']
    ordering = ['-start_time']
    
    fieldsets = (
        ('活动信息', {
            'fields': ('shelter', 'title', 'description', 'activity_type')
        }),
        ('时间和地点', {
            'fields': ('location', 'start_time', 'end_time', 'capacity')
        }),
        ('状态管理', {
            'fields': ('status', 'created_by')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ShelterStaff)
class ShelterStaffAdmin(admin.ModelAdmin):
    list_display = ['user', 'shelter', 'role', 'joined_at']
    list_filter = ['role', 'shelter']
    search_fields = ['user__username', 'shelter__name']
    ordering = ['-joined_at']

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ['donor', 'shelter', 'donation_type', 'amount', 'status', 'created_at']
    list_filter = ['donation_type', 'status', 'shelter']
    search_fields = ['donor__username', 'shelter__name']
    ordering = ['-created_at']
    
    fieldsets = (
        ('基础信息', {
            'fields': ('donor', 'shelter', 'donation_type')
        }),
        ('捐赠详情', {
            'fields': ('amount', 'goods_description', 'service_description')
        }),
        ('状态管理', {
            'fields': ('status', 'transaction_id')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']

@admin.register(InteractionApplication)
class InteractionApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'shelter', 'application_type', 'status', 'desired_date', 'created_at']
    list_filter = ['application_type', 'status', 'shelter']
    search_fields = ['applicant__username', 'shelter__name', 'purpose']
    ordering = ['-created_at']
    
    fieldsets = (
        ('申请信息', {
            'fields': ('applicant', 'shelter', 'animal', 'application_type')
        }),
        ('申请详情', {
            'fields': ('purpose', 'desired_date')
        }),
        ('状态管理', {
            'fields': ('status', 'reviewer', 'review_comments', 'reviewed_at')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'reviewed_at']
