from django.contrib import admin
from .models import Post, Comment, Notification, Report, ContentModeration, UserFeedback

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'views', 'likes', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    ordering = ['-created_at']
    
    fieldsets = (
        ('帖子信息', {
            'fields': ('title', 'author', 'category')
        }),
        ('内容', {
            'fields': ('content', 'images')
        }),
        ('统计数据', {
            'fields': ('views', 'likes')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'views', 'likes']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'author', 'content_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'author__username', 'post__title']
    ordering = ['-created_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '评论预览'
    
    fieldsets = (
        ('评论信息', {
            'fields': ('post', 'author')
        }),
        ('评论内容', {
            'fields': ('content',)
        }),
        ('时间信息', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']


@admin.register(UserFeedback)
class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'feedback_type', 'priority', 'title', 'status', 'created_at']
    list_filter = ['feedback_type', 'priority', 'status', 'created_at']
    search_fields = ['title', 'content', 'user__username']
    ordering = ['-created_at']
    
    fieldsets = (
        ('反馈信息', {
            'fields': ('user', 'feedback_type', 'priority')
        }),
        ('内容', {
            'fields': ('title', 'content', 'contact_info')
        }),
        ('处理状态', {
            'fields': ('status', 'admin_notes', 'processed_by')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at', 'processed_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['user', 'created_at', 'updated_at']
    
    def save_model(self, request, obj, form, change):
        # 如果是更新操作且设置了状态，自动记录处理人
        if change and 'status' in form.changed_data:
            if obj.status in ['resolved', 'dismissed']:
                obj.processed_by = request.user
                from django.utils import timezone
                obj.processed_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'sender', 'type', 'is_read', 'content_preview', 'created_at']
    list_filter = ['type', 'is_read', 'created_at']
    search_fields = ['content', 'recipient__username', 'sender__username']
    ordering = ['-created_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '通知内容预览'
    
    fieldsets = (
        ('通知信息', {
            'fields': ('recipient', 'sender', 'type')
        }),
        ('内容', {
            'fields': ('content', 'related_id')
        }),
        ('状态', {
            'fields': ('is_read',)
        }),
        ('时间信息', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']
