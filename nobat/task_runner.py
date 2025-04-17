import django
import logging
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nobat.settings")
django.setup()
##################


from django.conf import settings

import time
import multiprocessing
import threading

from user.models import User
from main.crawl import test_setup

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


def thread_task(thread_id):
    logger.info(f"Thread {thread_id} is starting")
    driver = test_setup()
    driver.get('https://softgozar.com')
    time.sleep(2)  # شبیه‌سازی کار که زمان می‌برد
    print(f"Thread {thread_id} is done")


# تابعی که در هر پراسس اجرا می‌شود
def process_task(process_id):
    print(f"Process {process_id} is starting")
    # ایجاد سه ترد در داخل هر پراسس
    threads = []
    for i in range(3):
        thread = threading.Thread(target=thread_task, args=(i,))
        threads.append(thread)
        thread.start()

    # منتظر ماندن برای پایان هر سه ترد
    for thread in threads:
        thread.join()
    print(f"Process {process_id} is done")


if __name__ == '__main__':
    logger.info(str(User))

    process = multiprocessing.Process(target=process_task, args=(1,))
    process.start()
    process.join()
