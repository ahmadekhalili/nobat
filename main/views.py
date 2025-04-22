import time

from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required

from rest_framework.views import APIView
from rest_framework.response import Response

import pytz
import sys
import redis
from datetime import datetime, timedelta
import logging as py_logging

from .crawl import *
from .methods import convert_jalali_to_gregorian, add_square, convert_str_jdatetime, get_datetime, maximize_chrome_window, minimize_chrome_window
from .models import Job, CrawlFuncArgs
from user.methods import remain_secs
from user.models import Customer, State, Town, Center,  ServiceType
#from nobat.celery import crawls_task


if not sys.platform.startswith('win'):
    r = redis.Redis(connection_pool=settings.REDIS_POOL)

logger = py_logging.getLogger('web')  # show in both celery and django console
cl_logging = py_logging.getLogger('celery')
tehran_tz = pytz.timezone('Asia/Tehran')


class test_celery(APIView):
    def get(self, request):
        from datetime import datetime, timedelta
        all,p = [],''
        dt = datetime.utcnow() + timedelta(seconds=6)
        #if all:
        #    with open('services.json', 'w', encoding='utf-8') as f:
        #        json.dump(all, f, ensure_ascii=False)
        return Response({'task_id': ''})


def index(request):
    if request.method == 'GET':
        logger.info("Task runnnnnnnnnnn")
        py_logging.info("Task runnnnnnnnnnn")
        return render(request, 'app1/index.html', {'product': 'p'})


active_browsers = {}
def crawl_func(customer_id, job_id, reserve_dates, reserve_times, test, title):
    # this func only tuns in job_runner via thread_task
    customer, report = Customer.objects.get(id=customer_id), []
    finall_message = ''  # clear up "no time/date message remains" message
    status = 'stop'   # for set in last
    driver = advance_setup()
    logger.info('started the crawl')
    # we dont want unwanted subsequnce requests came after complete crawl, to make status stop
    if customer.status == 'stop':
        customer.status = 'start'
        customer.save()
    logger.info('just runnig test')
    if False:
        r.incr(f'customer:{customer_id}:active_drivers')
        logger.info('----active browsers of user (celery env): %s', r.get(f'customer:{customer_id}:active_drivers'))
    else:
        if active_browsers.get(customer.id):
            active_browsers[customer.id] += [driver]
        else:
            active_browsers[customer.id] = [driver]
        logger.info(f'----active browsers of user (django env): {len(active_browsers[customer.id])}')
    if not hasattr(customer, 'drivers'):
        customer.drivers = [driver]
    else:
        customer.append(driver)
    success, finall_message = crawl_login(driver, job_id, str(customer.phone).strip(), customer.password, title), 'دریافت نوبت  موفقیت آمیز نبود دوباره تلاش کنید'
    if success:
        # driver.get('https://nobat.epolice.ir/?mod=search&city=614&subzone=616&specialty=13&vehicle=0')
        success = LocationStep(driver, report, title).run(customer)
        if success:
            success = CenterStep(driver, report, title).run(customer)
            if success:
                # only first index of date and times used for customer.customer_dates&time
                success_datetime = DateTimeStep(driver, report, title).run(dates=[reserve_dates], times=[[reserve_times]])  # each date can have several times here only one
                if not success_datetime[1]:   # time is better identifier is loop
                    if reserve_dates and reserve_times:
                        finall_message = "هیچ روز و ساعت خالی برای رزرو وجود ندارد"
                    else:
                        finall_message = "در روز/ساعت انتخابی نوبت خالی وجود ندارد"
                if success_datetime[0] and success_datetime[1]:
                    j_datetime = convert_str_jdatetime(success_datetime[0], success_datetime[1])
                    peigiry_path = LastStep(driver, report).run(customer, test)  # could be fals or message like: "شماره پیگیری: 03177711307"

                    if peigiry_path:  # (cd_peily, full_image_path), is False is seriouse fails
                        customer.cd_peigiri = peigiry_path[0] if peigiry_path[0] else "رزرو نوبت با مشخصات زیر با موفقیت در سامانه ثبت شد"  # we can fail getting cd_peigiry but success in reserve and take screenshot

                        logger.info("cd peigiry, image url to save in model: %s", peigiry_path)
                        customer.status = 'complete'
                        customer.finall_message = "رزرو نوبت با مشخصات زیر با موفقیت در سامانه ثبت شد"
                        logger.info("specefic selected date$time to save in customer model: %s", success_datetime)
                        if success_datetime[0] and success_datetime[1]:
                            customer.customer_date, customer.customer_time = success_datetime[0], success_datetime[1]
                        with open(peigiry_path[1], 'rb') as f:
                            # This ensures Django uses the 'upload_to' path and handles the file storage correctly.
                            customer.result_image.save(os.path.basename(peigiry_path[1]), File(f), save=True)
                        customer.save()
                        logger.info("everthing done successfully and saved to the model(customer)")
                        return True
                    else:
                        driver.quit()
                        customer.status = "stop"
                        customer.cd_peigiri = ""
                        customer.finall_message = finall_message
                        customer.save()
                        return False

    driver.quit()
    if False:
        r.decr(f'customer:{customer_id}:active_drivers')
    else:
        if active_browsers:
            active_browsers.popitem()
    if customer.status != 'complete':  # don't override the message in subsequence browsers came after successfull submit
        customer.finall_message = finall_message
        customer.status = status
        customer.save()
    return



class CrawlCustomer(APIView):
    #driver, message = crawl_login('09127761266', 'a13431343')
    def get(self, request, *args, **kwargs):
        customer = Customer.objects.get(id=request.GET['customer'])

        #driver = test_setup()
        #driver.get('https://nobat.epolice.ir/?mod=search&city=8&subzone=595&specialty=0&vehicle=0')
        report = []
        # crawl_login('09380851842', 'a13431343')
        # LocationStep(driver, report).run(customer)
        #CenterStep(driver, report).run(customer)
        p = None
        return Response()

    def post(self, request, *args, **kwargs):
        post = request.POST
        test = env.bool('TEST_RESERVATION', True)     # you can pass test=True for test porpuse (only finall submit not click)
        customer_id = post['customer']
        logger.info(f"form data: {request.POST}")
        dates_times = {f"{field}{i}": request.POST.get(f"{field}{i}", "") for field in ["time", "date"] for i in range(1, 5)}  # is like: time1,time2...,date1,date2..
        customer_time, customer_date = post.get('customer_time', ''), post.get('customer_date', '')  # customer_time like: 07:33  customer_date like: 1404/04/05

        customer = Customer.objects.filter(id=customer_id)
        pre_datetimes = [convert_jalali_to_gregorian(dates_times.get(f"date{i}"), dates_times.get(f"time{i}")) for i in range(1, 5)]
        datetimes = [date_time for date_time in pre_datetimes if date_time]
        logger.info("datetimes for schedules: %d", len(datetimes))
        add_square(customer_id, color_class='green')
        #customer.update(**dates_times, customer_time=customer_time, customer_date=customer_date)
        # pass customer_id, reserve_date, reserve_time to crawl_func(), if date and time is none, fastest time will be selected by crawl_func()
        crawl_func_args = CrawlFuncArgs.objects.create(customer_id=int(customer_id),
                                                       reserve_date=customer_date,
                                                       reserve_time=customer_time,
                                                       is_test=test)
        logger.info("crawl_func is created date: %s, time: %s", customer_date, customer_time)
        logger.info(f"datetimes: {datetimes}")
        if not datetimes:   # crawl now
            #crawl_func(customer_id, customer_date, customer_time, test, 'test_title')
            Job.objects.create(start_time=datetime.now(tehran_tz), status='wait', func_args=crawl_func_args)
            logger.info("job created successfully for now")

        else:              # crawl schedule date time
            for date_time in datetimes:
                date_time = date_time - timedelta(seconds=20)  # runs 1 minute faster because of login and captcha solve time wasting

                Job.objects.create(start_time=datetime.now(tehran_tz), status='wait', func_args=crawl_func_args)

                #jalali_date = jdatetime.datetime.fromgregorian(datetime=date_time)
                #task_date = jalali_date.strftime("%Y/%m/%d")
                #task_time = jalali_date.strftime("%H:%M")  # Format Time (HH:MM)
                #date_time_aware = tehran_tz.localize(date_time)
                #task1 = crawls_task.apply_async(args=[customer_id, customer_date, customer_time, test], eta=date_time_aware)
                #r.sadd(f'customer:{customer_id}:active_tasks', task1.id)
                #task2 = crawls_task.apply_async(args=[customer_id, customer_date, customer_time, test], eta=date_time_aware)
                logger.info("Celery rask created for run in: %s %s")
        return redirect('user:profile')  # رزرو موفقیت آمیر نبود دوباره تلاش کنید


class StopCrawl(APIView):
    def get(self, request, *args, **kwargs):
        customer = Customer.objects.get(id=request.GET['customer'])
        customer.color_classes = ''
        customer.status = 'stop'       # now customer can add another nobar reservation (afte complete status)
        customer.save()
        customer_active_browsers = active_browsers.get(customer.id, [])
        logger.info(f"----Active browsers to close: {len(customer_active_browsers)}")
        fails, success = 0, 0
        for driver in customer_active_browsers:
            try:
                driver.quit()
                success += 1
            except:
                fails += 1
        logger.info(f"----Failed closing: {fails}, success closing: {success}")
        active_browsers[customer.id] = []


        if not sys.platform.startswith('win'):  # in windows we have not redis and proper celery setup
            r.set(f'customer:{customer.id}:active_drivers', 0)
            logger.info(f"----active browsers of user (celery env) reset: 0")

            # Remove celery tasks forcely (panding or running tasks) completed
            task_ids = r.smembers(f'customer:{customer.id}:active_tasks')
            logger.info(f"----Active celery tasks to close: {len(task_ids)}")
            fails, success = 0, 0
            for task_id in task_ids:
                try:
                    app.control.revoke(task_id, terminate=True, signal='SIGKILL')
                    r.srem(f'customer:{customer.id}:active_tasks', task_id)
                    success += 1
                except:
                    fails += 1
            logger.info(f"----Failed closing celery: {fails}, success closing: {success}")

        return Response({'active_browsers': len(active_browsers)})


class States(APIView):
    def get(self, request, *args, **kwargs):
        states = [{'id': state.id, 'name': state.name} for state in State.objects.all()]
        return Response(states)

    def post(self, request, *args, **kwargs):
        return Response({'name': 'kagekkkkkkkkkkkkkk'})


class TownByState(APIView):
    def get(self, request, *args, **kwargs):
        state_id = request.GET['province']
        towns = State.objects.get(id=state_id).towns.all()
        dic = [{'id': town.id, 'name': town.name} for town in towns]
        return Response(dic)


class ServiceList(APIView):
    def get(self, request, *args, **kwargs):
        dic = [{'id': service.id, 'name': service.name} for service in ServiceType.objects.all()]
        return Response(dic)


class CentersByTownService(APIView):
    def get(self, request, *args, **kwargs):
        town_id, service_type_id = request.GET['town'], request.GET['service_type']
        centers = [{'id': center.id, 'name': center.title} for center in Center.objects.filter(towns__id=town_id, services__id=service_type_id, active=True)]
        return Response(centers)


@staff_member_required(login_url='/user/login')
def licence(request):
    if request.method == 'GET':
        try:
            if request.user.expiration_date:
                total_seconds = remain_secs(request.user.expiration_date)  # if total_seconds <=0 its expired (negative time)
                abs_seconds = abs(total_seconds)
                days = abs_seconds // 86400
            else:
                total_seconds = 0
                days = 0
            return render(request, 'app1/licence_time.html', {'days_remaining': days, 'secs_remaining': total_seconds})
        except:
            return redirect('user:profile')


class StartButtonSquares(APIView):
    def get(self, request, *args, **kwargs):
        customer = None
        if request.GET.get('customer'):
            customer = Customer.objects.get(id=request.GET['customer'])
            return Response({'square_colors': customer.color_classes})
        return Response()

    def post(self, request, customer_id=None, *args, **kwargs):
        customer_id, color_class = request.data.get('customer'), request.data['color_class']  # color_class 'green'|'red'
        add_square(customer_id, color_class)
        return Response()


def akh(title):
    while True:
        logger.info("akhhhhhhhhh")
        time.sleep(2)
    driver = test_setup()
    driver.get('https://softgozar.com')

    driver.quit()

import signal
import subprocess
class test(APIView):
    def get(self, request, *args, **kwargs):
        message, title = '', '1a'

        driver = test_setup()
        driver.get('https://softgozar.com/')
        wait = WebDriverWait(driver, 10)
        #chrome_pid = driver.service.process.pid
        #job = Job.objects.get(id=2)
        #job.status = 'finish'
        #job.save()
        logger.info(f"chrome_pid: {5}")
        #time.sleep(2)
        #windows = gw.getWindowsWithTitle(title)
        #print(CrawlFuncArgs.objects.get(id=2).get_reserve_dates_times())
        #os.kill(int(Job.objects.first().process_id), signal.SIGTERM)
        #subprocess.run([r'C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe',r'C:\Users\akh\Downloads\shared_folder\nobat\scripts\minimize_chrome.ahk'])
        time.sleep(20)

        return Response({'message response:': message})

    def post(self, request, customer_id=None, *args, **kwargs):
        return Response()


class BrowserIconList(APIView):
    def get(self, request, *args, **kwargs):
        # refresh and get new status by js every 2 sec (driver_id of 'fnish' job -> 'wait' should update (set via admin or...)
        jobs = Job.objects.exclude(status='close').filter(driver_process_id__isnull=False).values_list('driver_process_id', 'status')
        # Return dict: {id: status, ...} for JS consumption
        statuses = {str(id): status for id, status in jobs}
        # logger.info(f"id_status: {statuses}")
        return Response({'statuses': statuses})

    def post(self, request, customer_id=None, *args, **kwargs):
        driver_id = request.POST.get('id')  # is sent via js
        logger.info(f"js successfully posted to django view, driver id: {driver_id}")

        #request.session['last_driver_id'] = driver_id
        #real_driver_id = driver_id if driver_id else request.session['last_driver_id']
        #logger.info(f"id of driver for maximize window: {real_driver_id}")

        WindowsHandler.show_by_driver_id(driver_id)
        return Response()


class BrowserStatus(APIView):
    def get(self, request, *args, **kwargs):

        # Get active jobs: exclude closed, must have driver_process_id
        jobs = Job.objects.exclude(status='close').filter(driver_process_id__isnull=False).values_list('driver_process_id', 'status')
        # Return dict: {id: status, ...} for JS consumption
        statuses = {str(id): status for id, status in jobs}
        logger.info(f"statuses: {statuses}")
        return Response({'statuses': statuses})


class CloseBrowsers(APIView):
    def get(self, request, *args, **kwargs):
        return Response()
    def post(self, request, customer_id=None, *args, **kwargs):
        print("id of driver for set 'close' job")
        driver_id = request.session.get('last_driver_id')
        logger.info(f"id of the driver for set 'close' job: {driver_id}")
        if driver_id:
            job = Job.objects.get(driver_process_id=driver_id)
            job.status = 'close'
            job.save()
        return Response()
