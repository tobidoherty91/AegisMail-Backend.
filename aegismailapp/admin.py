from django.contrib import admin
from aegismailapp.models import AppIssueCounter


class AppIssueCounterAdmin(admin.ModelAdmin):
    list_display = ('id', 'crash_count', 'login_problem_count', 'data_syncing_issue_count')
    
# Register the AppIssueCounter model with the admin
admin.site.register(AppIssueCounter, AppIssueCounterAdmin)
