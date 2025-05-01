from django.conf import settings
from django.utils import timezone

from scheduler.models import Job
from main.models import OpenedBrowser

import logging
import multiprocessing
import threading
import pytz
import time
import string
import os

logger = logging.getLogger('web')
tehran_tz = pytz.timezone("Asia/Tehran")

'''
class TthreadTask:
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
'''

def thread_task(thread_number, job_id, crawl_func_run):  # thread_id used to set title of browser page
    args_obj = Job.objects.select_related('func_args').get(id=job_id).func_args
    #args_obj.title_ids = thread_id
    #args_obj.save()
    dates, times = [args_obj.reserve_date], [args_obj.reserve_time]
    o_b = OpenedBrowser.objects.first()
    if o_b:
        if not o_b.driver_number == 3:
            o_b.driver_number += 1
            o_b.save()
            logger.info(f"driver_number increased successfully")
        else:
            o_b.driver_number = 1
            o_b.save()
            logger.info(f"driver_number reset to 1")
    else:
        logger.error(f"plz create 1 instance of OpenedBrowser for start")
    logger.info(f"thread function: {thread_number} is going to run the function. job id: {job_id} args_obj: {args_obj}, status: {Job.objects.get(id=job_id).status}")
    crawl_func_run(args_obj.customer_id, job_id, dates, times, args_obj.is_test, o_b.driver_number)
    logger.info(f"thread function: {thread_number} is finished")
