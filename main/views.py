import time

from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required

from rest_framework.views import APIView
from rest_framework.response import Response

import pytz
import sys
import redis
from datetime import timedelta
import logging as py_logging
from celery import shared_task
from celery.utils.log import get_task_logger
from celery.result import AsyncResult

from .crawl import *
from .methods import convert_jalali_to_gregorian, add_square, convert_str_jdatetime
from user.methods import remain_secs
from user.models import Customer, State, Town, Center,  ServiceType
from nobat.celery import app


if not sys.platform.startswith('win'):
    r = redis.Redis(connection_pool=settings.REDIS_POOL)

logger = get_task_logger(__name__)
logging = py_logging.getLogger('explicit')  # show in both celery and django console
cl_logging = py_logging.getLogger('celery')


@shared_task
def sample_task():
    logger.info("AAAAAAAAA")
    logging.info("BBBBBBBBBB")
    py_logging.info("CCCCCCCCCCC")
    print("WWWWWWWWW")
    return True


class test_celery(APIView):
    def get(self, request):
        from datetime import datetime, timedelta
        all,p = [],''
        dt = datetime.utcnow() + timedelta(seconds=6)
        task = sample_task.apply_async(eta=dt)
        #if all:
        #    with open('services.json', 'w', encoding='utf-8') as f:
        #        json.dump(all, f, ensure_ascii=False)
        return Response({'task_id': task.id})


def index(request):
    if request.method == 'GET':
        logging.info("Task runnnnnnnnnnn")
        py_logging.info("Task runnnnnnnnnnn")
        return render(request, 'app1/index.html', {'product': 'p'})


active_browsers = {}
def crawl_func(customer_id, customer_date, customer_time, test, celery_task=False):
    customer, report = Customer.objects.get(id=customer_id), []
    finall_message = ''  # clear up "no time/date message remains" message
    status = 'stop'   # for set in last
    driver = setup()
    logging.info('started the crawl')
    # we dont want unwanted subsequnce requests came after complete crawl, to make status stop
    if customer.status == 'stop':
        customer.status = 'start'
        customer.save()
    logging.info('jsut runnig test')
    if celery_task:
        logging.info('free test')
        logging.info('test %s', str(r))
    if celery_task:
        r.incr(f'customer:{customer_id}:active_drivers')
        logging.info('----active browsers of user (celery env): %s', r.get(f'customer:{customer_id}:active_drivers'))
    else:
        if active_browsers.get(customer.id):
            active_browsers[customer.id] += [driver]
        else:
            active_browsers[customer.id] = [driver]
        logging.info('----active browsers of user (django env): ', len(active_browsers[customer.id]))
    if not hasattr(customer, 'drivers'):
        customer.drivers = [driver]
    else:
        customer.append(driver)
    success, finall_message = crawl_login(driver, str(customer.phone).strip(), customer.password), 'دریافت نوبت  موفقیت آمیز نبود دوباره تلاش کنید'
    if success:
        # driver.get('https://nobat.epolice.ir/?mod=search&city=614&subzone=616&specialty=13&vehicle=0')
        success = LocationStep(driver, report).run(customer)
        if success:
            success = CenterStep(driver, report).run(customer)
            if success:
                # only first index of date and times used for customer.customer_date&time
                success_datetime = DateTimeStep(driver, report).run(dates=[customer_date], times=[[customer_time]])  # each date can have several times here only one
                if not success_datetime[1]:   # time is better identifier is loop
                    if customer_date and customer_time:
                        finall_message = "هیچ روز و ساعت خالی برای رزرو وجود ندارد"
                    else:
                        finall_message = "در روز/ساعت انتخابی نوبت خالی وجود ندارد"
                if success_datetime[0] and success_datetime[1]:
                    j_datetime = convert_str_jdatetime(success_datetime[0], success_datetime[1])
                    peigiry_path = LastStep(driver, report).run(customer, test)  # could be fals or message like: "شماره پیگیری: 03177711307"

                    if peigiry_path:  # (cd_peily, full_image_path), is False is seriouse fails
                        customer.cd_peigiri = peigiry_path[0] if peigiry_path[0] else "رزرو نوبت با مشخصات زیر با موفقیت در سامانه ثبت شد"  # we can fail getting cd_peigiry but success in reserve and take screenshot

                        logging.info("cd peigiry, image url to save in model: %s", peigiry_path)
                        customer.status = 'complete'
                        customer.finall_message = "رزرو نوبت با مشخصات زیر با موفقیت در سامانه ثبت شد"
                        logging.info("specefic selected date$time to save in customer model: %s", success_datetime)
                        if success_datetime[0] and success_datetime[1]:
                            customer.customer_date, customer.customer_time = success_datetime[0], success_datetime[1]
                        with open(peigiry_path[1], 'rb') as f:
                            # This ensures Django uses the 'upload_to' path and handles the file storage correctly.
                            customer.result_image.save(os.path.basename(peigiry_path[1]), File(f), save=True)
                        customer.save()
                        logging.info("everthing done successfully and saved to the model(customer)")
                        return True
                    else:
                        driver.quit()
                        customer.status = "stop"
                        customer.cd_peigiri = ""
                        customer.finall_message = finall_message
                        customer.save()
                        return False

    driver.quit()
    if celery_task:
        r.decr(f'customer:{customer_id}:active_drivers')
    else:
        if active_browsers:
            active_browsers.popitem()
    if customer.status != 'complete':  # don't override the message in subsequence browsers came after successfull submit
        customer.finall_message = finall_message
        customer.status = status
        customer.save()
    return


@shared_task(bind=True)  # bind=True to access self (task instance)
def crawls_task(self, customer_id, customer_date, customer_time, test):
    add_square(customer_id, color_class='green')  # add square to start button of profile page
    res = crawl_func(customer_id, customer_date, customer_time, test, celery_task=True)
    r.srem(f'customer:{customer_id}:active_tasks', self.id)
    return res


class CrawlCustomer(APIView):
    #driver, message = crawl_login('09127761266', 'a13431343')
    def get(self, request, *args, **kwargs):
        customer = Customer.objects.get(id=request.GET['customer'])

        driver = setup()
        driver.get('https://nobat.epolice.ir/?mod=search&city=8&subzone=595&specialty=0&vehicle=0')
        report = []
        # crawl_login('09380851842', 'a13431343')
        # LocationStep(driver, report).run(customer)
        CenterStep(driver, report).run(customer)
        p = None
        return Response()

    def post(self, request, *args, **kwargs):
        post = request.POST
        test = env.bool('TEST_RESERVATION', True)     # you can pass test=True for test porpuse (only finall submit not click)
        customer_id = post['customer']
        logging.info(f"form data: {request.POST}")
        dates_times = {f"{field}{i}": request.POST.get(f"{field}{i}", "") for field in ["time", "date"] for i in range(1, 5)}  # is like: time1,time2...,date1,date2..
        customer_time, customer_date = post.get('customer_time', ''), post.get('customer_date', '')  # customer_time like: 07:33  customer_date like: 1404/4/5
        customer = Customer.objects.filter(id=customer_id)
        pre_datetimes = [convert_jalali_to_gregorian(dates_times.get(f"date{i}"), dates_times.get(f"time{i}")) for i in range(1, 5)]
        datetimes = [date_time for date_time in pre_datetimes if date_time]
        logging.info("datetimes for schedules: %d", len(datetimes))
        add_square(customer_id, color_class='green')
        customer.update(**dates_times, customer_time=customer_time, customer_date=customer_date)
        logging.info("dates updated, customer id: %s, datetimes: %s", customer_id, dates_times)
        if not datetimes:   # crawl normal inside django
            crawl_func(customer_id, customer_date, customer_time, test)
        else:              # crawl schedule date time by celery
            for date_time in datetimes:
                date_time = date_time - timedelta(minutes=1)  # runs 1 minute faster because of login and captcha solve time wasting
                jalali_date = jdatetime.datetime.fromgregorian(datetime=date_time)
                task_date = jalali_date.strftime("%Y/%m/%d")
                task_time = jalali_date.strftime("%H:%M")  # Format Time (HH:MM)
                local_tz = pytz.timezone('Asia/Tehran')
                date_time_aware = local_tz.localize(date_time)
                task1 = crawls_task.apply_async(args=[customer_id, customer_date, customer_time, test], eta=date_time_aware)
                r.sadd(f'customer:{customer_id}:active_tasks', task1.id)
                #task2 = crawls_task.apply_async(args=[customer_id, customer_date, customer_time, test], eta=date_time_aware)
                logging.info("Celery rask created for run in: %s %s", task_date, task_time)
        return redirect('user:profile')  # رزرو موفقیت آمیر نبود دوباره تلاش کنید


class StopCrawl(APIView):
    def get(self, request, *args, **kwargs):
        customer = Customer.objects.get(id=request.GET['customer'])
        customer.color_classes = ''
        customer.status = 'stop'       # now customer can add another nobar reservation (afte complete status)
        customer.save()
        customer_active_browsers = active_browsers.get(customer.id, [])
        logging.info(f"----Active browsers to close: {len(customer_active_browsers)}")
        fails, success = 0, 0
        for driver in customer_active_browsers:
            try:
                driver.quit()
                success += 1
            except:
                fails += 1
        logging.info(f"----Failed closing: {fails}, success closing: {success}")
        active_browsers[customer.id] = []


        if not sys.platform.startswith('win'):  # in windows we have not redis and proper celery setup
            r.set(f'customer:{customer.id}:active_drivers', 0)
            logging.info(f"----active browsers of user (celery env) reset: 0")

            # Remove celery tasks forcely (panding or running tasks) completed
            task_ids = r.smembers(f'customer:{customer.id}:active_tasks')
            logging.info(f"----Active celery tasks to close: {len(task_ids)}")
            fails, success = 0, 0
            for task_id in task_ids:
                try:
                    app.control.revoke(task_id, terminate=True, signal='SIGKILL')
                    r.srem(f'customer:{customer.id}:active_tasks', task_id)
                    success += 1
                except:
                    fails += 1
            logging.info(f"----Failed closing celery: {fails}, success closing: {success}")

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

