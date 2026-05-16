from django.apps import AppConfig


class HostlerPanelConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Hostlers_panel"

    def ready(self):
        import Hostlers_panel.signals