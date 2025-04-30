from django.conf import settings
from django.utils import timezone

from main.models import Job, OpenedBrowser
from main.views import crawl_func, akh
from main.crawl import setup

import logging
import os
import multiprocessing
import threading
import pytz
import time
import string

from main.crawl import setup_funcs

logger = logging.getLogger('web')
tehran_tz = pytz.timezone("Asia/Tehran")


class TtthreadTask:
    def __init__(self, threads_count, process_number, job_id, fun_to_run):
        try:
            self.thread = {job_id: threading.Thread(target=thread_task, args=(process_number, job_id, fun_to_run))}
            logger.info(f"{threads_count} threads instance created.")
        except Exception as e:
            logger.error(f"{len(self.threads)}/{threads_count} threads failed to create. error {e}")

    def run(self):
        logger.info(f"Process is started")
        for job_id, thread in self.threads.items():
            thread.start()
            logger.info(f"thread {job_id} started .start()")

        for job_id, thread in self.threads.items():
            thread.join()


def thread_task(i):  # thread_id used to set title of browser page
    driver = setup_funcs[i]()
    driver.get("https://softgozar.com")
    time.sleep(5)


def multy_thread(job_id, thread_count=2):
    print("multy_thread just started")
    logger.info("multy_thread just started, logger")
    threads_list = []
    for i in range(thread_count):
        thread = threading.Thread(target=thread_task, args=(i+1,))
        logger.info(f"thread {i} instance created.")
        threads_list.append(thread)
        thread.start()
        logger.info(f"thread {i} started .start()")

    # منتظر ماندن برای پایان هر سه ترد
    for thread in threads_list:
        thread.join()


