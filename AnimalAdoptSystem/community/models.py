from django.db import models
from django.conf import settings

class Post(models.Model):
    title = models.CharField(max_length=100, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='作者')
    category = models.CharField(max_length=50, verbose_name='分类')
    images = models.JSONField(default=list, verbose_name='图片URL列表')
    views = models.IntegerField(default=0, verbose_name='浏览量')
    likes = models.IntegerField(default=0, verbose_name='点赞数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'community_posts'
        verbose_name = '帖子'
        verbose_name_plural = '帖子列表'

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='帖子')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='评论者')
    content = models.TextField(verbose_name='评论内容')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name='父评论')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='评论时间')

    class Meta:
        db_table = 'community_comments'
        verbose_name = '评论'
        verbose_name_plural = '评论列表'

    def __str__(self):
        return f'{self.author.username} - {self.content[:20]}'

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('like', '点赞'),
        ('comment', '评论'),
        ('system', '系统通知'),
        ('adoption', '领养状态更新'),
    )
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='接收者')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications', verbose_name='发送者')
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, verbose_name='通知类型')
    content = models.TextField(verbose_name='通知内容')
    related_id = models.IntegerField(null=True, blank=True, verbose_name='相关对象ID')
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'community_notifications'
        verbose_name = '通知'
        verbose_name_plural = '通知列表'

    def __str__(self):
        return f'{self.recipient.username} - {self.get_type_display()}'


class Report(models.Model):
    REPORT_TYPES = (
        ('post', '帖子'),
        ('comment', '评论'),
        ('user', '用户'),
    )
    REASON_CHOICES = (
        ('spam', '垃圾信息'),
        ('harassment', '骚扰'),
        ('inappropriate', '不当内容'),
        ('copyright', '版权侵犯'),
        ('other', '其他'),
    )
    STATUS_CHOICES = (
        ('pending', '待处理'),
        ('reviewing', '审核中'),
        ('resolved', '已解决'),
        ('dismissed', '已驳回'),
    )
    
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports_made', verbose_name='举报人')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, verbose_name='举报类型')
    target_id = models.IntegerField(verbose_name='目标对象ID')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES, verbose_name='举报原因')
    description = models.TextField(verbose_name='详细描述')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='处理状态')
    moderator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports_handled', verbose_name='处理人')
    resolution_notes = models.TextField(blank=True, null=True, verbose_name='处理说明')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='举报时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    resolved_at = models.DateTimeField(blank=True, null=True, verbose_name='解决时间')

    class Meta:
        db_table = 'community_reports'
        verbose_name = '举报记录'
        verbose_name_plural = '举报记录列表'

    def __str__(self):
        return f'{self.reporter.username} 举报 {self.report_type} #{self.target_id}'


class ContentModeration(models.Model):
    MODERATION_ACTIONS = (
        ('approve', '批准'),
        ('reject', '拒绝'),
        ('delete', '删除'),
        ('warn', '警告'),
        ('ban', '封禁'),
    )
    
    moderator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='审核员')
    content_type = models.CharField(max_length=20, choices=[('post', '帖子'), ('comment', '评论')], verbose_name='内容类型')
    content_id = models.IntegerField(verbose_name='内容 ID')
    action = models.CharField(max_length=20, choices=MODERATION_ACTIONS, verbose_name='操作类型')
    reason = models.TextField(verbose_name='操作原因')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')

    class Meta:
        db_table = 'content_moderation'
        verbose_name = '内容审核记录'
        verbose_name_plural = '内容审核记录列表'

    def __str__(self):
        return f'{self.moderator.username} {self.get_action_display()} {self.content_type} #{self.content_id}'


class UserFeedback(models.Model):
    FEEDBACK_TYPES = (
        ('complaint', '投诉'),
        ('suggestion', '建议'),
        ('bug', 'Bug 反馈'),
        ('other', '其他'),
    )
    PRIORITY_CHOICES = (
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
    )
    STATUS_CHOICES = (
        ('pending', '待处理'),
        ('reviewing', '处理中'),
        ('resolved', '已解决'),
        ('dismissed', '已驳回'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedbacks', verbose_name='反馈用户')
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES, verbose_name='反馈类型')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name='优先级')
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='详细内容')
    contact_info = models.CharField(max_length=100, blank=True, null=True, verbose_name='联系方式（选填）')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='处理状态')
    admin_notes = models.TextField(blank=True, null=True, verbose_name='管理员备注')
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_feedbacks', verbose_name='处理人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    processed_at = models.DateTimeField(blank=True, null=True, verbose_name='处理时间')
    
    class Meta:
        db_table = 'user_feedbacks'
        verbose_name = '用户反馈'
        verbose_name_plural = '用户反馈列表'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.get_feedback_type_display()} - {self.title}'

