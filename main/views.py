import time

from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required

from rest_framework.views import APIView
from rest_framework.response import Response

import logging
from celery import shared_task
from celery.utils.log import get_task_logger


from .crawl import *
from .methods import convert_jalali_to_gregorian
from user.methods import remain_secs
from user.models import Customer, State, Town, Center,  ServiceType

logger = get_task_logger(__name__)


@shared_task
def sample_task():
    logging.info("Task runnnnnnnnnnn")
    print("Task runnnnnnnnnnn")
    return None

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
        print('0000000')
        driver = setup()
        print('111111111')
        driver.get('https://google.com')
        return render(request, 'app1/index.html', {'product': 'p'})


active_browsers = {}
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
        print('form data: ', request.POST)
        dates_times = {f"{field}{i}": request.POST.get(f"{field}{i}", "") for field in ["time", "date"] for i in range(1, 5)}  # is like: time1,time2...,date1,date2..
        customer_time, customer_date = post.get('customer_time', ''), post.get('customer_date', '')
        print('customer date and time: ', customer_date, customer_time)
        customer, report = Customer.objects.filter(id=request.POST['customer']), []
        customer.update(**dates_times, customer_time=customer_time, customer_date=customer_date)
        datetimes = [convert_jalali_to_gregorian(dates_times.get(f"date{i}"), dates_times.get(f"time{i}")) for i in range(1, 5)]
        customer = customer[0]
        driver = setup()
        if active_browsers.get(customer.id):
            active_browsers[customer.id] += [driver]
        else:
            active_browsers[customer.id] = [driver]
        print('----active browsers of user: ', len(active_browsers[customer.id]))
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
                    success = DateTimeStep(driver, report).run(dates=[customer_date], times=[[customer_time]])  # each date can have several times here only one
                    if not success:
                        if customer_date and customer_time:
                            finall_message =  "هیچ روز و ساعت خالی برای روز وجود ندارد"
                        else:
                            finall_message = "در روز/ساعت انتخابی نوبت خالی وجود ندارد"
                    if success:
                        print('active browsers: ', len(active_browsers))
                        cd_peigiry_message = LastStep(driver, report).run(customer)  # could be fals or message like: "شماره پیگیری: 03177711307"

                        if cd_peigiry_message:
                            customer.status = 'complete'
                            finall_message = "با موفقیت ثبت شد"
                            customer.cd_peigiri = cd_peigiry_message
                            customer.save()
                            return Response()
                        else:
                            driver.quit()
                            customer.status = 'stop'
                            customer.save()
                            return Response()
            #DateTimeStep(driver, report).run(date_time='')
        driver.quit()
        if customer.status != 'complete':  # don't override the message in subsequence browsers came after successfull submit
            customer.finall_message = finall_message
        customer.status = 'stop'

        customer.save()
        return redirect('user:profile')  # رزرو موفقیت آمیر نبود دوباره تلاش کنید


class StopCrawl(APIView):
    def get(self, request, *args, **kwargs):
        customer = Customer.objects.get(id=request.GET['customer'])
        customer.color_classes = ''
        customer.save()
        customer_active_browsers = active_browsers.get(customer.id, [])
        print(f"----Active browsers to close: {len(customer_active_browsers)}")
        fails, success = 0, 0
        for driver in customer_active_browsers:
            try:
                driver.quit()
                success += 1
            except:
                fails += 1
        print(f"----Failed closing: {fails}, success closing: {success}")
        active_browsers[customer.id] = []
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
        if request.user.expiration_date:
            total_seconds = remain_secs(request.user.expiration_date)  # if total_seconds <=0 its expired (negative time)
            abs_seconds = abs(total_seconds)
            days = abs_seconds // 86400
        else:
            total_seconds = 0
            days = 0
        return render(request, 'app1/licence_time.html', {'days_remaining': days, 'secs_remaining': total_seconds})


class StartButtonSquares(APIView):
    def get(self, request, *args, **kwargs):
        customer = None
        if request.GET.get('customer'):
            customer = Customer.objects.get(id=request.GET['customer'])
            return Response({'square_colors': customer.color_classes})
        return Response()

    def post(self, request, *args, **kwargs):
        customer_id, color_class = request.data['customer'], request.data['color_class']  # color_class 'green'|'red'
        customer = Customer.objects.get(id=customer_id)  # sent via ajax not form post
        if customer.color_classes:
            customer.color_classes = customer.color_classes + f",{color_class}"
        else:
            customer.color_classes = color_class
        customer.save()
        return Response()

