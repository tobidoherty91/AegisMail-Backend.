from celery import shared_task
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import SecurityEventLog
from .utils import detect_suspicious_activity
from .notifications import notify_user_of_security_event
import logging

logger = logging.getLogger(__name__)

@shared_task
def check_security_events():
    """
    Periodically checks for suspicious activities for all users
    and sends notifications if any are detected.
    """
    try:
        users = User.objects.filter(is_active=True)  # Process only active users
        suspicious_count = 0

        for user in users:
            is_suspicious, message = detect_suspicious_activity(user.email)
            if is_suspicious:
                # Log the event
                SecurityEventLog.objects.create(
                    event_type="Suspicious Activity",
                    user_email=user.email,
                    ip_address=None,  # Include IP if available
                    timestamp=timezone.now()
                )
                
                # Notify the user
                notify_user_of_security_event(user, {
                    'event_type': "Suspicious Activity",
                    'message': message
                })
                suspicious_count += 1

        logger.info(f"Security check completed. Suspicious activities detected: {suspicious_count}")
        return f"Security check completed. {suspicious_count} suspicious activities detected."

    except Exception as e:
        logger.error(f"Error during security check: {e}")
        return f"Error during security check: {e}"
