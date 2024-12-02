from django.apps import AppConfig

class AegismailappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aegismailapp'

    def ready(self):
        # Importing the signals to ensure they are registered
        try:
            import aegismailapp.signals  # Ensure signals are registered
            print("Aegismailapp is ready")
        except Exception as e:
            print(f"Error during app initialization: {e}")
