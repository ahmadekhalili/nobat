from django.conf import settings

import os
from celery import Celery
import logging.config


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nobat.settings')

# Create the Celery app instance.
app = Celery('nobat')

# Use Django's settings module for Celery configuration using a namespace.
# This means all Celery-related configuration keys in settings.py should be prefixed with CELERY_.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Explicitly configure logging using Django settings
logging.config.dictConfig(settings.LOGGING)

# Automatically discover tasks from all installed Django apps.
app.autodiscover_tasks()

# Optional: A debug task to verify the Celery setup.
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')