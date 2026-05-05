from django.db import models
from users.models import User
from animals.models import Animal

class AdoptionApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', '待审核'),
        ('approved', '审核通过'),
        ('rejected', '审核拒绝'),
        ('completed', '已领养'),
        ('cancelled', '已取消'),
    )
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='申请人')
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, verbose_name='申请领养的动物')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='申请状态')
    application_reason = models.TextField(verbose_name='申请原因')
    personal_info = models.TextField(verbose_name='个人情况说明')
    contact_phone = models.CharField(max_length=11, verbose_name='联系电话')
    contact_address = models.CharField(max_length=200, verbose_name='联系地址')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='申请时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='审核时间')
    review_comments = models.TextField(null=True, blank=True, verbose_name='审核意见')
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_applications', verbose_name='审核人')

    class Meta:
        db_table = 'adoption_applications'
        verbose_name = '领养申请'
        verbose_name_plural = '领养申请列表'

    def __str__(self):
        return f'{self.applicant.username} - {self.animal.name}'

class AdoptionMatch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, verbose_name='动物')
    match_score = models.FloatField(verbose_name='匹配分数')
    match_reason = models.TextField(verbose_name='匹配原因')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'adoption_matches'
        verbose_name = '领养匹配'
        verbose_name_plural = '领养匹配列表'

    def __str__(self):
        return f'{self.user.username} - {self.animal.name} ({self.match_score})'


class CloudPetActivity(models.Model):
    """云养宠物动态记录"""
    ACTIVITY_TYPES = (
        ('feeding', '喂食'),
        ('medical', '医疗'),
        ('playing', '玩耍'),
        ('grooming', '美容'),
        ('exercise', '运动'),
        ('other', '其他'),
    )
    
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='cloud_activities', verbose_name='动物')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES, verbose_name='活动类型')
    title = models.CharField(max_length=100, verbose_name='标题')
    content = models.TextField(verbose_name='详细内容')
    images = models.JSONField(default=list, blank=True, verbose_name='图片列表')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='posted_activities', verbose_name='发布者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='发布时间')
    
    class Meta:
        db_table = 'cloud_pet_activities'
        verbose_name = '云养宠物动态'
        verbose_name_plural = '云养宠物动态列表'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.animal.name} - {self.title}'

