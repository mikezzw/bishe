from django.db import models

class Animal(models.Model):
    STATUS_CHOICES = (
        ('available', '可领养'),
        ('adopted', '已领养'),
        ('pending', '审核中'),
        ('medical', '医疗中'),
    )
    GENDER_CHOICES = (
        ('male', '公'),
        ('female', '母'),
        ('unknown', '未知'),
    )
    SPECIES_CHOICES = (
        ('cat', '猫'),
        ('dog', '狗'),
        ('other', '其他'),
    )
    name = models.CharField(max_length=50, verbose_name='动物名称')
    species = models.CharField(max_length=20, choices=SPECIES_CHOICES, default='cat', verbose_name='物种')
    breed = models.CharField(max_length=50, verbose_name='品种')
    age = models.IntegerField(verbose_name='年龄(月)')
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='unknown', verbose_name='性别')
    weight = models.FloatField(verbose_name='体重(kg)')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name='状态')
    description = models.TextField(verbose_name='描述')
    personality = models.TextField(verbose_name='性格特点')
    health_status = models.TextField(verbose_name='健康状况')
    images = models.JSONField(default=list, verbose_name='图片URL列表')
    found_place = models.CharField(max_length=200, verbose_name='发现地点')
    found_date = models.DateField(verbose_name='发现日期')
    shelter = models.ForeignKey('shelters.Shelter', on_delete=models.SET_NULL, null=True, blank=True, related_name='animals', verbose_name='所属基地')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'animals'
        verbose_name = '流浪动物'
        verbose_name_plural = '流浪动物列表'

    # 动物性格特征 (1-5分)
    animal_openness = models.FloatField(default=3.0, help_text="动物开放性")
    animal_conscientiousness = models.FloatField(default=3.0, help_text="动物尽责性")
    animal_extraversion = models.FloatField(default=3.0, help_text="动物外向性")
    animal_agreeableness = models.FloatField(default=3.0, help_text="动物宜人性")
    animal_neuroticism = models.FloatField(default=3.0, help_text="动物神经质")

    def __str__(self):
        return self.name
