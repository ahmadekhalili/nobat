from django.apps import AppConfig

import os


class SchedulerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scheduler'

    def ready(self):
        if os.environ.get('RUN_MAIN', None) != 'true':
            return  # Prevents double execution on runserver
        from .scheduler import scheduler  # Ensures scheduler starts
