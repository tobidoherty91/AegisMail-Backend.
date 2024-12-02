"""
URL configuration for aegismail project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

# Define a simple view to handle `/api/`
def api_overview(request):
    return JsonResponse({
        "routes": [
            "/api/token/",
            "/api/token/refresh/",
            "/login/",
            "/register/",
            "/security-events/",
            "/log-event/",
            "/issues/",
            "/api/issue-counters/",
            "/webhook/",
            "/update-device-token/",
        ]
    })

# Home view
def home(request):
    return JsonResponse({"message": "Welcome to AegisMail!"})

urlpatterns = [
    path('', home, name='home'),  # Root path
    path('admin/', admin.site.urls),
    path("api/", include("aegismailapp.urls")),  
    path('api/overview/', api_overview, name='api_overview'),  
]

