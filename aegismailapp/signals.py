from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Ensures a UserProfile is created or updated whenever a User is saved.
    """
    try:
        if created:
            UserProfile.objects.create(user=instance)
            logger.info(f"UserProfile created for user: {instance.username}")
        else:
            profile, created = UserProfile.objects.get_or_create(user=instance)
            if not created:
                profile.save()  # Update existing profile
            logger.info(f"UserProfile updated for user: {instance.username}")
    except Exception as e:
        logger.error(f"Error in create_or_update_user_profile: {e}")
