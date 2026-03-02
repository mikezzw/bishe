from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('normal', '普通用户'),
        ('volunteer', '志愿者'),
        ('shelter', '动物基地'),
        ('admin', '管理员'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='normal')
    phone = models.CharField(max_length=11, blank=True, null=True)
    avatar = models.URLField(blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    shelter = models.OneToOneField('shelters.Shelter', on_delete=models.SET_NULL, null=True, blank=True, related_name='manager', verbose_name='管理的基地')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户列表'

    # OCEAN人格特质分数 (1-5分)
    openness = models.FloatField(default=3.0, help_text="开放性")
    conscientiousness = models.FloatField(default=3.0, help_text="尽责性")
    extraversion = models.FloatField(default=3.0, help_text="外向性")
    agreeableness = models.FloatField(default=3.0, help_text="宜人性")
    neuroticism = models.FloatField(default=3.0, help_text="神经质")