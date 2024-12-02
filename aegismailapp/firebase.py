import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
import os

# Initialize Firebase Admin SDK
def initialize_firebase():
    """
    Initialize Firebase Admin SDK only once.
    """
    try:
        # Path to your Firebase service account credentials
        cred_path = os.path.join(settings.BASE_DIR, 'google-services.json')  # Ensure this is the correct path
        cred = credentials.Certificate(cred_path)

        # Initialize Firebase only if it hasn't been initialized yet
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
            print("Firebase Admin SDK initialized successfully.")
        else:
            print("Firebase Admin SDK already initialized.")
    except Exception as e:
        print(f"Error initializing Firebase: {e}")

# Function to send push notifications
def send_notification_to_user(token, title, body):
    """
    Send a notification to a specific device using Firebase Cloud Messaging (FCM).

    :param token: The recipient's device FCM token.
    :param title: Notification title.
    :param body: Notification body text.
    """
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=token,
        )

        # Send the message to the device
        response = messaging.send(message)
        print(f"Successfully sent message: {response}")
    except Exception as e:
        print(f"Error sending notification: {e}")

# Initialize Firebase as the app starts
initialize_firebase()
