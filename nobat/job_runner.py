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

from user.models import User
from main.models import Job
from main.crawl import test_setup
from main.views import akh, crawl_func

log_dir = os.path.join(settings.BASE_DIR, 'logs')
os.makedirs(log_dir, exist_ok=True)           # if django_root/logs not exists, create that folder, otherwise skip
log_file_path = os.path.join(log_dir, 'threads.log')  # this also create threads.log if was not exists.

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

tehran_tz = pytz.timezone("Asia/Tehran")
letters = list(string.ascii_lowercase + string.ascii_uppercase)


def thread_task(thread_id, job_id, fun_to_run):  # thread_id used to set title of browser page
    args_obj = Job.objects.select_related('func_args').get(id=job_id).func_args
    #args_obj.title_ids = thread_id
    #args_obj.save()
    dates, times = args_obj.get_reserve_dates_times()

    logger.info(f"thread function: {thread_id} is starting. job id: {job_id} args_obj: {args_obj}")
    fun_to_run(args_obj.customer_id, job_id, dates, times, args_obj.is_test, thread_id)
    logger.info(f"thread function: {thread_id} is finished")


# تابعی که در هر پراسس اجرا می‌شود
def process_task(process_number, threads_count, job_id, fun_to_run):
    logger.info("11111111")
    print(f"Process {process_number} is starting")
    # ایجاد سه ترد در داخل هر پراسس
    threads = []
    for i in range(threads_count):
        thread_id = f"{process_number}{letters[i]}"
        thread = threading.Thread(target=thread_task, args=(thread_id, job_id, fun_to_run))
        threads.append(thread)
        thread.start()

    # منتظر ماندن برای پایان هر سه ترد
    for thread in threads:
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
    process_number = 1   # just for title of the page
    while True:
        now_tehran = timezone.now().astimezone(tehran_tz)
        running_jobs = Job.objects.filter(start_time__lt=now_tehran, status='wait')
        time.sleep(2)
        total = running_jobs.count()
        processes = []

        for start in range(0, total, bath):
            batched_jobs = running_jobs[start:start + bath]
            # پردازش هر batch
            for i, job in enumerate(batched_jobs):
                process = multiprocessing.Process(target=process_task, args=(process_number, threads, job.id, crawl_func))
                process.start()
                job.process_id = process.pid
                job.save()
                processes.append(process)
                process_number += 1

        for process in processes:
            process.join()
