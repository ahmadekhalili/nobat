import django
import logging
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nobat.settings")
django.setup()
#####################################


from django.utils import timezone
from django.conf import settings
import multiprocessing
import threading
import pytz
import time

from user.models import User
from main.models import Job
from main.crawl import test_setup
from main.views import akh

BASE_DIR = settings.BASE_DIR
log_file_path = os.path.join(BASE_DIR, 'logs', f'threads.log')
if not os.path.exists(log_file_path):
    os.makedirs(log_file_path)

logging.basicConfig(
    level=logging.DEBUG,  # سطح لاگ‌ها
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # فرمت لاگ‌ها
    handlers=[
        logging.FileHandler(log_file_path),  # ذخیره لاگ در فایل
        logging.StreamHandler()  # نمایش لاگ در کنسول
    ]
)
logger = logging.getLogger(__name__)

tehran_tz = pytz.timezone("Asia/Tehran")


def thread_task(thread_id, fun_to_run):
    logger.info(f"Thread {thread_id} is starting")
    fun_to_run()
    time.sleep(2)  # شبیه‌سازی کار که زمان می‌برد
    print(f"Thread {thread_id} is done")


# تابعی که در هر پراسس اجرا می‌شود
def process_task(process_id, threads_nums, fun_to_run):
    print(f"Process {process_id} is starting")
    # ایجاد سه ترد در داخل هر پراسس
    threads = []
    for i in range(threads_nums):
        thread = threading.Thread(target=thread_task, args=(i, fun_to_run))
        threads.append(thread)
        thread.start()

    # منتظر ماندن برای پایان هر سه ترد
    for thread in threads:
        thread.join()
    print(f"Process {process_id} is done")


if __name__ == '__main__':
    logger.info(str(Job))
    bath = 5
    threads_nums = 1
    while True:
        now_tehran = timezone.now().astimezone(tehran_tz)
        expired_jobs = Job.objects.filter(start_date__lt=now_tehran)
        total = expired_jobs.count()
        process = []

        for start in range(0, total, bath):
            batched_jobs = expired_jobs[start:start + bath]
            # پردازش هر batch
            for i, job in enumerate(batched_jobs):
                process = multiprocessing.Process(target=process_task, args=(i, threads_nums, akh))
                process.start()
                process.append(process)

        for process in process:
            process.join()
