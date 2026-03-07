from rest_framework import serializers
from .models import Post, Comment, Notification, Report, ContentModeration, UserFeedback
from users.serializers import UserSerializer

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = '__all__'

class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('title', 'content', 'category', 'images')

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        post = Post.objects.create(**validated_data)
        return post

class PostUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('title', 'content', 'category', 'images')

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = '__all__'
    
    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []

class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('post', 'content', 'parent')

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        comment = Comment.objects.create(**validated_data)
        return comment

class NotificationSerializer(serializers.ModelSerializer):
    recipient = UserSerializer(read_only=True)
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = '__all__'

class NotificationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('is_read',)


class ReportSerializer(serializers.ModelSerializer):
    reporter = UserSerializer(read_only=True)
    moderator = UserSerializer(read_only=True)
    
    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ('reporter', 'status', 'moderator', 'resolved_at')


class ReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ('report_type', 'target_id', 'reason', 'description')
    
    def create(self, validated_data):
        validated_data['reporter'] = self.context['request'].user
        return super().create(validated_data)


class ReportUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ('status', 'resolution_notes')
    
    def update(self, instance, validated_data):
        # 更新处理人和解决时间
        if 'status' in validated_data and validated_data['status'] in ['resolved', 'dismissed']:
            validated_data['moderator'] = self.context['request'].user
            from django.utils import timezone
            validated_data['resolved_at'] = timezone.now()
        return super().update(instance, validated_data)


class ContentModerationSerializer(serializers.ModelSerializer):
    moderator = UserSerializer(read_only=True)
    
    class Meta:
        model = ContentModeration
        fields = '__all__'
        read_only_fields = ('moderator',)


class UserFeedbackSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    processed_by = UserSerializer(read_only=True)
    
    class Meta:
        model = UserFeedback
        fields = '__all__'
        read_only_fields = ('user', 'status', 'processed_by', 'processed_at')


class UserFeedbackCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFeedback
        fields = ('feedback_type', 'priority', 'title', 'content', 'contact_info')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class UserFeedbackUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFeedback
        fields = ('status', 'admin_notes')
    
    def update(self, instance, validated_data):
        # 更新处理人和解决时间
        if 'status' in validated_data and validated_data['status'] in ['resolved', 'dismissed']:
            validated_data['processed_by'] = self.context['request'].user
            from django.utils import timezone
            validated_data['processed_at'] = timezone.now()
        return super().update(instance, validated_data)
