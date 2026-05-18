import os
from celery import Celery

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "StayEase.settings"
)

app = Celery("StayEase")

app.config_from_object(
    "django.conf:settings",
    namespace="CELERY"
)

app.autodiscover_tasks()

app.conf.beat_schedule = {

    "generate-monthly-bills": {

        "task":
        "Hostlers_panel.tasks.generate_monthly_bills",

        "schedule": 86400.0,
    },

    "create-meal-charges-every-5-minutes": {

        "task":
        "Hostlers_panel.tasks.create_meal_charges",

        "schedule": 300.0,
    },
}