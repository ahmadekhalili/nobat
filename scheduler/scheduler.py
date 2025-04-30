from django.conf import settings

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from urllib.parse import quote_plus

from pathlib import Path
import environ
import logging
import os

logger = logging.getLogger('web')


# Get the root path of the project
#BASE_DIR = Path(__file__).resolve().parents[2]  # Go up 2 levels to reach `nobat/`
env = environ.Env()
env.read_env(os.path.join(settings.BASE_DIR, '.env'))


username = env('POSTGRES_USERNAME')
password = quote_plus(env('POSTGRES_USERPASS'))  # encode special chars
dbname = env('POSTGRES_DBNAME')
jobstores = {
    'default': SQLAlchemyJobStore(url=f"postgresql://{username}:{password}@localhost:5432/{dbname}")
}

logger.info(f"apscheduler going to start")
scheduler = BackgroundScheduler(jobstores=jobstores)
scheduler.start()

logger.info(f"apscheduler started")
