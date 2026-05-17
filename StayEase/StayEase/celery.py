import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StayEase.settings')

app = Celery('StayEase')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {

    "lock-expired-meals-every-5-minutes": {

        "task":
            "Base_Panel.tasks.lock_expired_meals",

        "schedule": 300.0,
    },
}