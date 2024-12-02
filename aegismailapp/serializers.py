from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import SecurityEventLog, AppIssue, UserProfile

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        help_text='Password',
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        try:
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password']
            )
        except Exception as e:
            raise serializers.ValidationError({'error': str(e)})
        return user

class SecurityEventLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityEventLog
        fields = ['event_type', 'timestamp', 'user_email', 'ip_address']

class AppIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppIssue
        fields = ['issue_type', 'description', 'occurrence_count', 'last_reported']

class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['user', 'device_token']
