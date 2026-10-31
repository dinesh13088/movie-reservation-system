import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie_services.settings')

app = Celery('movie_services')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
