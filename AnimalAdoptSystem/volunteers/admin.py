from django.contrib import admin
from .models import VolunteerProfile, VolunteerTask, VolunteerActivity, ActivityParticipant

@admin.register(VolunteerProfile)
class VolunteerProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'gender', 'age', 'education', 'status', 'created_at']
    list_filter = ['gender', 'education', 'status']
    search_fields = ['name', 'user__username', 'skills', 'occupation']
    ordering = ['-created_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'name', 'gender', 'age')
        }),
        ('教育背景', {
            'fields': ('education', 'occupation')
        }),
        ('志愿者信息', {
            'fields': ('skills', 'availability')
        }),
        ('详细信息', {
            'fields': ('experience', 'motivation')
        }),
        ('状态管理', {
            'fields': ('status',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']

@admin.register(VolunteerTask)
class VolunteerTaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'location', 'status', 'assigned_to', 'start_time', 'created_by']
    list_filter = ['status', 'start_time']
    search_fields = ['title', 'description', 'location']
    ordering = ['-created_at']
    
    fieldsets = (
        ('任务信息', {
            'fields': ('title', 'description', 'location')
        }),
        ('时间安排', {
            'fields': ('start_time', 'end_time')
        }),
        ('人员安排', {
            'fields': ('required_skills', 'assigned_to', 'created_by')
        }),
        ('状态管理', {
            'fields': ('status',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']

@admin.register(VolunteerActivity)
class VolunteerActivityAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'status', 'organizer', 'capacity', 'start_time']
    list_filter = ['status', 'start_time']
    search_fields = ['name', 'description', 'location']
    ordering = ['-created_at']
    
    fieldsets = (
        ('活动信息', {
            'fields': ('name', 'description', 'location')
        }),
        ('时间安排', {
            'fields': ('start_time', 'end_time', 'capacity')
        }),
        ('组织信息', {
            'fields': ('organizer',)
        }),
        ('状态管理', {
            'fields': ('status',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ActivityParticipant)
class ActivityParticipantAdmin(admin.ModelAdmin):
    list_display = ['activity', 'participant', 'status', 'registered_at']
    list_filter = ['status', 'registered_at']
    search_fields = ['activity__name', 'participant__username']
    ordering = ['-registered_at']
