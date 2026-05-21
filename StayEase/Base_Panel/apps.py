# hostels/apps.py
from django.apps import AppConfig

class HostelsConfig(AppConfig):
    name = "Base_Panel"

    def ready(self):
        import Base_Panel.signals  