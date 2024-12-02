from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.shortcuts import render
from django.views.generic import ListView
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
import json
import datetime

from .models import SecurityEventLog, AppIssueCounter
from .serializers import UserSerializer, UserProfileSerializer, SecurityEventLogSerializer, AppIssueSerializer, AppIssue
from .notifications import send_notification, notify_user_of_security_event
from .oauth import get_google_credentials
from .utils import detect_suspicious_activity



# --- Home Views ---
def home(request):
    return HttpResponse("Welcome to AegisMail!")

# --- User Management ---
class RegisterUserView(generics.CreateAPIView):
    """Register a new user."""
    queryset = User.objects.all()
    serializer_class = UserSerializer


@csrf_exempt
def login_view(request):
    """Handle login request with JWT token generation."""
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            })
        return Response({"error": "Invalid credentials"}, status=400)
    return JsonResponse({'message': 'Invalid request method'}, status=400)


@login_required
def protected_view(request):
    return JsonResponse({
        "message": "You have accessed a protected API endpoint."
    })

@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })
    return Response({"error": "Invalid credentials"}, status=400)

def register_user(request):
    if request.method == 'POST':
        # Process registration data
        return JsonResponse({'message': 'User registered successfully!'})
    return JsonResponse({'error': 'Invalid request method!'}, status=400)

   
# --- Google OAuth ---
def google_login(request):
    """Handle Google login and return the OAuth token."""
    try:
        credentials = get_google_credentials()
        return JsonResponse({"token": credentials.token})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# --- Security Event Logging ---
class SecurityEventList(generics.ListAPIView):
    """List all security events for the authenticated user."""
    permission_classes = [IsAuthenticated]
    serializer_class = SecurityEventLogSerializer

    def get_queryset(self):
        return SecurityEventLog.objects.filter(user_email=self.request.user.email)


class LogSecurityEventView(APIView):
    """Log security events and detect suspicious activity."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        event_type = request.data.get('event_type')
        event_data = request.data.get('event_data')
        ip_address = request.META.get('REMOTE_ADDR')
        device_info = request.META.get('HTTP_USER_AGENT', 'Unknown')

        try:
            event = SecurityEventLog.objects.create(
                event_type=event_type,
                user_email=request.user.email,
                event_data=event_data,
                ip_address=ip_address,
                device_info=device_info
            )
            is_suspicious, message = detect_suspicious_activity(request.user.email)
            if is_suspicious:
                send_notification(request.user, message)

            return JsonResponse({'status': 'Event logged'}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


# --- Webhook Listener ---
def webhook_listener(request):
    """Handle incoming webhooks for security events."""
    if request.method == "POST":
        try:
            event_data = json.loads(request.body)
            notify_user_of_security_event(
                user_token=event_data.get("user_token"),
                event_details="Suspicious activity detected: " + event_data.get("event")
            )
            return JsonResponse({"message": "Webhook received successfully"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid method"}, status=400)


# --- App Issue Management ---
class IssueCounterAPIView(APIView):
    """View to fetch and update app issue counters."""
    
    def get(self, request):
        issue_counter = AppIssueCounter.objects.first()
        if issue_counter:
            return Response({
                'crash_count': issue_counter.crash_count,
                'login_problem_count': issue_counter.login_problem_count,
                'data_syncing_issue_count': issue_counter.data_syncing_issue_count
            })
        return Response({"error": "No data found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        issue_type = request.data.get('issue_type')
        issue_counter, created = AppIssueCounter.objects.get_or_create(id=1)

        if issue_type == 'crash':
            issue_counter.crash_count += 1
        elif issue_type == 'login_problem':
            issue_counter.login_problem_count += 1
        elif issue_type == 'data_syncing':
            issue_counter.data_syncing_issue_count += 1
        else:
            return Response({"error": "Invalid issue type"}, status=status.HTTP_400_BAD_REQUEST)

        issue_counter.save()
        return Response({
            "message": f"Successfully updated {issue_type} counter",
            "crash_count": issue_counter.crash_count,
            "login_problem_count": issue_counter.login_problem_count,
            "data_syncing_issue_count": issue_counter.data_syncing_issue_count
        })


def report_issue(request):
    """Report an app issue."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            issue_type = data.get("issue_type")
            description = data.get("description")
            log_app_issue(issue_type, description)
            return JsonResponse({"message": "Issue logged successfully"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid method"}, status=400)


# --- Utility Functions ---
def log_app_issue(issue_type, description):
    """Log app issues to the database."""
    issue, created = AppIssueCounter.objects.get_or_create(id=1)

    if issue_type == 'crash':
        issue.crash_count += 1
    elif issue_type == 'login_problem':
        issue.login_problem_count += 1
    elif issue_type == 'data_syncing':
        issue.data_syncing_issue_count += 1

    issue.save()


def store_log(action, details):
    """Store logs in MongoDB."""
    try:
        from .db import get_collection
        logs_collection = get_collection('logs')
        logs_collection.insert_one({
            "action": action,
            "details": details,
            "timestamp": datetime.datetime.now()
        })
    except Exception as e:
        print(f"Error storing log: {e}")


# --- Profile Management ---
class UpdateDeviceTokenView(generics.UpdateAPIView):
    """Update the user's device token."""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.userprofile

class AppIssueList(ListView):
    model = AppIssue
    template_name = 'aegismailapp/app_issues.html'  # Create this template
    context_object_name = 'issues'
    
    
    