from django.db import models
from users.models import User

class VolunteerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, verbose_name='用户')
    name = models.CharField(max_length=50, verbose_name='姓名')
    gender = models.CharField(max_length=10, choices=[('male', '男'), ('female', '女')], verbose_name='性别')
    age = models.IntegerField(verbose_name='年龄')
    education = models.CharField(max_length=50, verbose_name='学历')
    occupation = models.CharField(max_length=100, verbose_name='职业')
    skills = models.CharField(max_length=200, verbose_name='技能特长')
    availability = models.CharField(max_length=200, verbose_name='可服务时间')
    experience = models.TextField(blank=True, null=True, verbose_name='志愿者经历')
    motivation = models.TextField(blank=True, null=True, verbose_name='志愿服务动机')
    status = models.CharField(max_length=20, choices=[('pending', '待审核'), ('approved', '已通过'), ('rejected', '已拒绝')], default='pending', verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'volunteer_profiles'
        verbose_name = '志愿者资料'
        verbose_name_plural = '志愿者资料列表'

    def __str__(self):
        return f'{self.name} - {self.user.username}'

class VolunteerTask(models.Model):
    TASK_STATUS = (
        ('pending', '待分配'),
        ('assigned', '已分配'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    )
    title = models.CharField(max_length=100, verbose_name='任务标题')
    description = models.TextField(verbose_name='任务描述')
    location = models.CharField(max_length=200, verbose_name='任务地点')
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')
    required_skills = models.CharField(max_length=200, verbose_name='所需技能')
    status = models.CharField(max_length=20, choices=TASK_STATUS, default='pending', verbose_name='任务状态')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks', verbose_name='分配给')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks', verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'volunteer_tasks'
        verbose_name = '志愿者任务'
        verbose_name_plural = '志愿者任务列表'

    def __str__(self):
        return self.title

class VolunteerActivity(models.Model):
    ACTIVITY_STATUS = (
        ('planning', '策划中'),
        ('upcoming', '即将开始'),
        ('ongoing', '进行中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    )
    name = models.CharField(max_length=100, verbose_name='活动名称')
    description = models.TextField(verbose_name='活动描述')
    location = models.CharField(max_length=200, verbose_name='活动地点')
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')
    capacity = models.IntegerField(verbose_name='参与人数上限')
    status = models.CharField(max_length=20, choices=ACTIVITY_STATUS, default='planning', verbose_name='活动状态')
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_activities', verbose_name='组织者')
    shelter = models.ForeignKey('shelters.Shelter', on_delete=models.CASCADE, related_name='shelter_activities', null=True, blank=True, verbose_name='所属基地')
    participants = models.ManyToManyField(User, through='ActivityParticipant', related_name='participated_activities', verbose_name='参与者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'volunteer_activities'
        verbose_name = '志愿者活动'
        verbose_name_plural = '志愿者活动列表'

    def __str__(self):
        return self.name

class ActivityParticipant(models.Model):
    activity = models.ForeignKey(VolunteerActivity, on_delete=models.CASCADE, verbose_name='活动')
    participant = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='参与者')
    status = models.CharField(max_length=20, choices=[('registered', '已报名'), ('attended', '已参加'), ('absent', '未参加')], default='registered', verbose_name='参与状态')
    registered_at = models.DateTimeField(auto_now_add=True, verbose_name='报名时间')

    class Meta:
        db_table = 'activity_participants'
        verbose_name = '活动参与者'
        verbose_name_plural = '活动参与者列表'
        unique_together = ('activity', 'participant')

    def __str__(self):
        return f'{self.participant.username} - {self.activity.name}'

