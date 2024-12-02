from django.contrib.auth.models import User  # Or use get_user_model if a custom User model
from django.db import models
from django.utils import timezone

# Model to log security events (e.g., login attempts, password changes)
class SecurityEventLog(models.Model):
    event_type = models.CharField(max_length=100)  # Event type (e.g., Login Attempt, MFA Change)
    timestamp = models.DateTimeField(auto_now_add=True)  # Automatically set the time of the event
    user_email = models.EmailField()  # Email associated with the event
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # Optional IP address for the event

    def __str__(self):
        return f'{self.event_type} - {self.user_email}'


# App-related issues (e.g., crashes, bugs)
class AppIssue(models.Model):
    issue_type = models.CharField(max_length=255)
    description = models.TextField()
    occurrence_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.issue_type


# Model to store OAuth credentials for different providers (e.g., Google, Yahoo)
class OAuthCredentials(models.Model):
    PROVIDERS = [
        ('google', 'Google'),
        ('yahoo', 'Yahoo'),
        ('microsoft', 'Microsoft')
    ]
    provider = models.CharField(max_length=20, choices=PROVIDERS)  # Provider name
    access_token = models.TextField()  # Access token for authentication
    refresh_token = models.TextField(null=True, blank=True)  # Optional refresh token
    expires_at = models.DateTimeField()  # Expiration time of the access token

    def __str__(self):
        return f'{self.provider} credentials'


# User profile to store device token for push notifications
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')  # One-to-one with User
    device_token = models.CharField(max_length=255, null=True, blank=True)  # Optional FCM token for notifications

    def __str__(self):
        return f'{self.user.username} Profile'


# A model to count app issues (e.g., crashes, login problems, data syncing issues)
class AppIssueCounter(models.Model):
    crash_count = models.IntegerField(default=0)
    login_problem_count = models.IntegerField(default=0)
    data_syncing_issue_count = models.IntegerField(default=0)

    def __str__(self):
        return f'App Issue Counter - Crashes: {self.crash_count}, Login Issues: {self.login_problem_count}, Data Sync Issues: {self.data_syncing_issue_count}'


# A test model (for development or debugging purposes)
class TestModel(models.Model):
    name = models.CharField(max_length=100)  # Simple name field

    def __str__(self):
        return self.name
