import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")

app = Celery("core_sinapum")

# Lê CELERY_* do settings.py
app.config_from_object("django.conf:settings", namespace="CELERY")

# Autodiscover tasks em apps Django e também nos seus services
app.autodiscover_tasks()
