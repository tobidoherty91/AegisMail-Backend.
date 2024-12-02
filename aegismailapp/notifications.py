import logging
from firebase_admin import messaging

logger = logging.getLogger(__name__)

def notify_user_of_security_event(user, event_data):
    """
    Notify the user of a security event by sending a push notification.

    :param user: The user to notify
    :param event_data: Data related to the security event (e.g., suspicious activity details)
    """
    try:
        device_token = user.userprofile.device_token  # Assumes user has a UserProfile with a device_token field
        if not device_token:
            logger.warning("No device token for user: %s", user.username)
            return

        if not all(key in event_data for key in ('event_type', 'message')):
            raise ValueError("Missing required keys in event_data: 'event_type', 'message'")

        title = 'Security Alert'
        body = f"Event: {event_data['event_type']} - {event_data['message']}"

        send_notification(device_token, title, body)
    except Exception as e:
        logger.error(f"Error notifying user of security event: {e}")

def send_notification(token, title, body):
    """
    Send a notification to a specific device.

    :param token: The recipient's device FCM token
    :param title: Notification title
    :param body: Notification body
    """
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token,
    )
    try:
        response = messaging.send(message)
        logger.info(f"Successfully sent message: {response}")
    except messaging.FirebaseError as e:
        logger.error(f"Firebase error sending notification: {e}")
    except Exception as e:
        logger.error(f"Error sending notification: {e}")
