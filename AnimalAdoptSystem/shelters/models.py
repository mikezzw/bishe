from django.db import models
from users.models import User
from animals.models import Animal

class Shelter(models.Model):
    name = models.CharField(max_length=100, verbose_name='基地名称')
    description = models.TextField(verbose_name='基地描述')
    address = models.CharField(max_length=200, verbose_name='基地地址')
    contact_name = models.CharField(max_length=50, verbose_name='联系人')
    contact_phone = models.CharField(max_length=11, verbose_name='联系电话')
    email = models.EmailField(verbose_name='邮箱')
    website = models.URLField(blank=True, null=True, verbose_name='网站')
    capacity = models.IntegerField(verbose_name='容纳能力')
    current_animals = models.IntegerField(default=0, verbose_name='当前动物数量')
    status = models.CharField(max_length=20, choices=[('active', '活跃'), ('inactive', '不活跃')], default='active', verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'shelters'
        verbose_name = '动物基地'
        verbose_name_plural = '动物基地列表'

    def __str__(self):
        return self.name

class ShelterActivity(models.Model):
    ACTIVITY_TYPES = (
        ('adoption', '领养活动'),
        ('volunteer', '志愿者活动'),
        ('fundraising', '筹款活动'),
        ('education', '教育活动'),
        ('other', '其他活动'),
    )
    STATUS_CHOICES = (
        ('upcoming', '即将开始'),
        ('ongoing', '进行中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    )
    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE, related_name='activities', verbose_name='所属基地')
    title = models.CharField(max_length=100, verbose_name='活动标题')
    description = models.TextField(verbose_name='活动描述')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES, verbose_name='活动类型')
    location = models.CharField(max_length=200, verbose_name='活动地点')
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')
    capacity = models.IntegerField(verbose_name='参与人数上限')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming', verbose_name='活动状态')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'shelter_activities'
        verbose_name = '基地活动'
        verbose_name_plural = '基地活动列表'

    def __str__(self):
        return self.title

class ShelterStaff(models.Model):
    ROLES = (
        ('manager', '管理员'),
        ('staff', '工作人员'),
        ('volunteer', '志愿者'),
    )
    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE, related_name='staff', verbose_name='所属基地')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shelter_roles', verbose_name='用户')
    role = models.CharField(max_length=20, choices=ROLES, verbose_name='角色')
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name='加入时间')

    class Meta:
        db_table = 'shelter_staff'
        verbose_name = '基地工作人员'
        verbose_name_plural = '基地工作人员列表'
        unique_together = ('shelter', 'user')

    def __str__(self):
        return f'{self.user.username} - {self.shelter.name} ({self.get_role_display()})'

class Donation(models.Model):
    DONATION_TYPES = (
        ('money', '金钱'),
        ('goods', '物品'),
        ('service', '服务'),
    )
    STATUS_CHOICES = (
        ('pending', '待处理'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    )
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations', blank=True, null=True, verbose_name='捐赠人')
    donor_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='捐赠人姓名')
    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE, related_name='donations', verbose_name='接收基地')
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='捐赠金额')
    goods_description = models.TextField(blank=True, null=True, verbose_name='捐赠物品描述')
    service_description = models.TextField(blank=True, null=True, verbose_name='捐赠服务描述')
    donation_type = models.CharField(max_length=20, choices=DONATION_TYPES, verbose_name='捐赠类型')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='交易ID')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='捐赠时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'shelters_donation'
        verbose_name = '捐赠记录'
        verbose_name_plural = '捐赠记录列表'

    def __str__(self):
        # 处理donor为None的情况，使用donor_name字段作为备选
        donor_name = self.donor.username if self.donor else self.donor_name or '匿名捐赠人'
        if self.donation_type == 'money':
            return f'{donor_name} - {self.shelter.name} - ¥{self.amount}'
        else:
            return f'{donor_name} - {self.shelter.name} - {self.get_donation_type_display()}'


class DonationUsage(models.Model):
    USAGE_TYPES = (
        ('food', '食物采购'),
        ('medical', '医疗费用'),
        ('facility', '设施建设'),
        ('staff', '人员工资'),
        ('other', '其他用途'),
    )
    
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE, related_name='usages', verbose_name='对应捐赠')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='使用金额')
    usage_type = models.CharField(max_length=20, choices=USAGE_TYPES, verbose_name='使用类型')
    purpose = models.CharField(max_length=200, verbose_name='使用目的')
    description = models.TextField(verbose_name='详细说明')
    attachments = models.JSONField(default=list, verbose_name='相关凭证文件')
    approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_usages', verbose_name='审批人')
    usage_date = models.DateField(verbose_name='使用日期')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'shelters_donationusage'
        verbose_name = '捐赠使用记录'
        verbose_name_plural = '捐赠使用记录列表'
    
    def __str__(self):
        return f'{self.donation} - {self.purpose} - ¥{self.amount}'
    
    def clean(self):
        from django.core.exceptions import ValidationError
        # 检查使用金额不超过捐赠金额
        if self.donation.donation_type == 'money':
            total_used = sum(usage.amount for usage in self.donation.usages.exclude(pk=self.pk))
            if total_used + self.amount > (self.donation.amount or 0):
                raise ValidationError('使用金额不能超过捐赠金额')

class InteractionApplication(models.Model):
    APPLICATION_TYPES = (
        ('visit', '探访'),
        ('volunteer', '志愿服务'),
        ('foster', '寄养'),
        ('other', '其他'),
    )
    STATUS_CHOICES = (
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
        ('completed', '已完成'),
    )
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interaction_applications', verbose_name='申请人')
    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE, related_name='interaction_applications', verbose_name='申请基地')
    animal = models.ForeignKey(Animal, on_delete=models.SET_NULL, null=True, blank=True, related_name='interaction_applications', verbose_name='相关动物')
    application_type = models.CharField(max_length=20, choices=APPLICATION_TYPES, verbose_name='申请类型')
    purpose = models.TextField(verbose_name='申请目的')
    desired_date = models.DateTimeField(verbose_name='期望日期')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    review_comments = models.TextField(blank=True, null=True, verbose_name='审核意见')
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_interaction_applications', verbose_name='审核人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='申请时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    reviewed_at = models.DateTimeField(blank=True, null=True, verbose_name='审核时间')

    class Meta:
        db_table = 'interaction_applications'
        verbose_name = '互动申请'
        verbose_name_plural = '互动申请列表'

    def __str__(self):
        return f'{self.applicant.username} - {self.shelter.name} - {self.get_application_type_display()}'

