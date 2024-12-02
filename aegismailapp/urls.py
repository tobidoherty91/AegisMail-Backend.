from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    home,
    google_login,
    RegisterUserView,
    SecurityEventList,
    LogSecurityEventView,
    AppIssueList,
    IssueCounterAPIView,
    webhook_listener,
    UpdateDeviceTokenView,
    login_view,
    protected_view,
)

app_name = "aegismailapp"  # Namespace for the app

urlpatterns = [
    # API overview (if necessary here, otherwise remove)
    path('', home, name='home'),  # Local app homepage

    # JWT Authentication endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', login_view, name='login'),  # Standard login endpoint

    # User management
    path('register/', RegisterUserView.as_view(), name='register_user'),  # Single registration endpoint
    path('google-login/', google_login, name='google_login'),  # Google login

    # Security events
    path('security-events/', SecurityEventList.as_view(), name='security_events'),
    path('log-event/', LogSecurityEventView.as_view(), name='log_event'),

    # App issues
    path('issues/', AppIssueList.as_view(), name='app_issues'),
    path('issue-counters/', IssueCounterAPIView.as_view(), name='issue_counter_api'),

    # Protected endpoint
    path('protected/', protected_view, name='protected_view'),

    # Webhook and device token management
    path('webhook/', webhook_listener, name='webhook_listener'),
    path('update-device-token/', UpdateDeviceTokenView.as_view(), name='update_device_token'),
]
