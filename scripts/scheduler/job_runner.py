import django
import logging
import os
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(BASE_DIR))  # Add project root to sys.path to find nobat.settings auto from it

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nobat.settings")
django.setup()
###############################


from main.models import Job, CrawlFuncArgs
from .scheduler import scheduler

from datetime import datetime


def schedule_custom_job(run_date, task_type, data):
    CustomJob.objects.create(
        job_id=job_id,
        run_date=run_date,
        task_type=task_type,
        data=data,
    )

    # Register with APScheduler
    scheduler.add_job(
        func=my_task,
        trigger='date',
        run_date=run_date,
        kwargs={
            'task_type': task_type,
            'data': data
        },
        id=str(job_id),
        replace_existing=True
    )

