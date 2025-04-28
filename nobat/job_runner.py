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
import string

from main.models import Job, OpenedBrowser
from main.views import crawl_func, akh


log_dir = os.path.join(settings.BASE_DIR, 'logs')
os.makedirs(log_dir, exist_ok=True)           # if django_root/logs not exists, create that folder, otherwise skip
log_file_path = os.path.join(log_dir, 'threads.log')  # this also create threads.log if was not exists.

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

tehran_tz = pytz.timezone("Asia/Tehran")
letters = list(string.ascii_lowercase + string.ascii_uppercase)


def thread_task(thread_number, job_id, fun_to_run):  # thread_id used to set title of browser page
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
        logger.error(f"create first instance of OpenedBrowser")
    logger.info(f"thread function: {thread_number} is going to run the function. job id: {job_id} args_obj: {args_obj}, status: {Job.objects.get(id=job_id).status}")
    fun_to_run(args_obj.customer_id, job_id, dates, times, args_obj.is_test, o_b.driver_number)
    logger.info(f"thread function: {thread_number} is finished")


# تابعی که در هر پراسس اجرا می‌شود
class ProcessTask:
    def __init__(self, threads_count, process_number, job_ids, fun_to_run):
        self.threads = {}
        try:
            self.threads = {job_id: threading.Thread(target=thread_task, args=(process_number, job_id, fun_to_run)) for job_id in job_ids}
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


def process_task(process_number, threads_count, job_id, fun_to_run):
    logger.info(f"Process {process_number} is running")
    #from django.db import connection
    #connection.close()
    # ایجاد سه ترد در داخل هر پراسس
    threads_list = []

    for i in range(threads_count):
        thread = threading.Thread(target=thread_task, args=(process_number, job_id, fun_to_run))
        logger.info(f"thread {i} instance created.")
        threads_list.append(thread)
        thread.start()
        logger.info(f"thread {i} started .start()")

    # منتظر ماندن برای پایان هر سه ترد
    for thread in threads_list:
        thread.join()

    # After all threads complete, mark job as finished
    try:
        job = Job.objects.get(id=job_id)
        job.status = 'finish'
        job.save()
        logger.info(f"Job id {job_id} marked as finished")
    except Job.DoesNotExist:
        logger.error(f"Job id {job_id} not found")
    logger.info(f"Process {process_number} is done")


if __name__ == '__main__':
    logger.info('job_runner.py started.')
    bath = 5
    threads = 1
    process_number = 0   # just for title of the page
    while True:
        now_tehran = timezone.now().astimezone(tehran_tz)
        running_jobs = list(Job.objects.filter(start_time__lt=now_tehran, status='wait'))
        time.sleep(2)
        total = len(running_jobs)
        processes = []

        for start in range(0, total, bath):
            batched_jobs = running_jobs[start:start + bath]
            # پردازش هر batch
            logger.info(f"number of threads to start at the same time: {batched_jobs}")
            job_ids = [job.id for job in batched_jobs]
            process_task_ob = ProcessTask(len(job_ids), process_number, job_ids, crawl_func)
            for job in batched_jobs:
                job.process_id = process_task_ob.threads[job.id].ident
                job.save()

            process_task_ob.run()
            '''
            process_task(process_number, threads, job.id, crawl_func)
            for i, job in enumerate(batched_jobs):
                process = threading.Thread(target=process_task, args=(process_number, threads, job.id, crawl_func))
                process.start()
                logger.info(f"Process {process_number} .start() called, (may not run)")
                job.process_id = process.ident
                job.save()
                processes.append(process)
                process_number += 1
            '''

