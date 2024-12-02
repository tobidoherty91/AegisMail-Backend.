from .models import SecurityEventLog
from django.utils import timezone
from datetime import timedelta
import logging

# Initialize a logger for suspicious activity
logger = logging.getLogger(__name__)

def detect_suspicious_activity(user_email, time_window_hours=1, ip_threshold=3):
    """
    Detect suspicious activity based on recent security events such as multiple login attempts
    from different IP addresses within a short time frame.

    Args:
    - user_email (str): The email address of the user to check for suspicious activity.
    - time_window_hours (int): Time window in hours to check for events (default: 1 hour).
    - ip_threshold (int): Number of distinct IP addresses to flag as suspicious (default: 3).

    Returns:
    - Tuple[bool, str]: Returns a tuple containing a boolean indicating whether suspicious activity was detected,
                        and a message providing further details if applicable.
    """
    try:
        # Define the time window to check for recent events
        time_threshold = timezone.now() - timedelta(hours=time_window_hours)

        # Fetch the user's recent login attempts from the database
        recent_events = SecurityEventLog.objects.filter(
            user_email=user_email,
            event_type='Login Attempt',
            event_time__gte=time_threshold
        )

        # Extract distinct IP addresses from the recent login attempts
        ip_addresses = recent_events.values_list('ip_address', flat=True).distinct()

        # Check if the count of distinct IPs exceeds the threshold
        if ip_addresses.count() > ip_threshold:
            message = f"Suspicious activity detected: Multiple login attempts from {ip_addresses.count()} distinct IP addresses."
            logger.warning(f"Suspicious activity for {user_email}: {message}")
            return True, message

        # Add more detection rules here if necessary

        # No suspicious activity detected
        return False, ""
    except Exception as e:
        logger.error(f"Error detecting suspicious activity for {user_email}: {e}")
        return False, f"Error occurred during detection: {e}"
