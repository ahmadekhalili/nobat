from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.admin.views.decorators import staff_member_required

from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt

from jdatetime import datetime as jdatetime
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

import json

from .models import *
from .methods import generate_activation_code
from .serializers import *


def login_account(request):
    user, message, message_status = object(), "", 0
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('user:profile')
        return render(request, 'app1/login.html', {'message': message, 'message_status': message_status})

    elif request.method == 'POST':
        data = request.POST
        user = authenticate(request, username=data['username'], password=data['password'])
        if user is not None:
            login(request, user)
            if request.user.is_staff:
                message, message_status = ".ورود با موفقیت انجام شد", 2
                return redirect('user:profile')
            else:
                message, message_status = "کاربر فعال نمی باشد", 1
        else:
            message, message_status = "کد ملی یا پسورد اشتباه است.", 1
        return render(request, 'app1/login.html', {'user': user, 'message': message, 'message_status': message_status})


def login_account2(request):    # telegram logint happens here (auto from referesh token) (value send via js in login.html)
    user, message, message_status = object(), "", 0
    if request.method == 'GET':
        return render(request, 'app1/login.html', {'message': message, 'message_status': message_status})

    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        access_token = AccessToken(data['token'])
        user_id = access_token.get('user_id')
        user = User.objects.get(pk=user_id)

        # If tokens are valid, log the user in using Django's session
        login(request, user)  # from django.contrib.auth import login
        return redirect('user:profile')


def logout_account(request):
    if request.method == 'GET':
        logout(request)

        refresh_token = request.POST.get('refresh_token')
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            print("Token already blacklisted or invalid:", e)
        return redirect('user:login')


def activate(request, pk):
    if request.method == 'GET':
        user, message_status = User.objects.get(id=pk), 0
        return render(request, 'app1/activate_form.html', {'user': user, 'message_status': message_status})

    if request.method == 'POST':
        data, message_status = request.POST, 0
        message, user = "", object()

        if data['status'] == '1':
            user = authenticate(request, username=data['cdmeli'], password=data['password'])
            if user is not None:
                # logout(request)
                login(request, user)
                user.active_code = generate_activation_code()
                user.save()
            else:
                message, message_status = "کد ملی یا پسورد اشتباه است.", 1
        elif data['status'] == '2' and request.user.is_authenticated:
            user = request.user
            if not user.is_staff:    # maybe superuser came here
                message_status = 2
                user.is_staff = True
                user.save()
                message = f".کاربر با کد ملی {user.username} با موفقیت فعال شد"
        return render(request, 'app1/activate_form.html', {'user': user, 'message': message, 'message_status': message_status})

def test(request):
    return render(request, 'app1/index.html', {'product': 'p'})

class Protected(APIView):
    def get(self, request):
        user = request.user
        data = {
            'message': f'Hello, {user.username}. You have accessed a protected endpoint.',
            'user_id': user.id,
            'email': user.username,
        }
        return Response(data)


#@staff_member_required(login_url='/user/login')
def profile(request):
    customer_time_slots = [f"{hour:02d}:{minute:02d}" for hour in range(7, 17) for minute in range(0, 60, 10) if not (hour == 16 and minute > 0)]
    time_slots = [f"{hour:02d}:{minute:02d}" for hour in range(0, 24) for minute in range(0, 60, 10)]
    if request.user.is_authenticated:
        if request.user.expiration_date and request.user.expiration_date < jdatetime.now():
            return render(request, 'app1/licence_time.html', {})
        elif not request.user.is_staff:
            return render(request, 'app1/licence_time.html', {})
        else:
            if request.method == 'GET':  # 'user' auto fills in templates if user logged in
                message_status = 0
                if request.GET.get('customer'):
                    customer = Customer.objects.get(id=request.GET['customer'])
                else:
                    customer = None
                return render(request, 'app1/profile_page.html', {'customer': customer, 'time_slots': time_slots, 'customer_time_slots': customer_time_slots})
    else:
        return redirect('user:login')



@staff_member_required(login_url='/user/login')
def reserved_customers(request):
    if request.user and request.user.is_authenticated:
        if request.user.expiration_date and request.user.expiration_date < jdatetime.now():
            return render(request, 'app1/licence_time.html', {})
    if request.method == 'GET':
        try:
            customers = request.user.customers.filter(status='complete')
            return render(request, 'app1/customer_list.html', {'customers': customers})
        except:
            redirect('user:profile')


@staff_member_required(login_url='/user/login')
def customer_detail(request, pk):
    if request.user and request.user.is_authenticated:
        if request.user.expiration_date and request.user.expiration_date < jdatetime.now():
            return render(request, 'app1/licence_time.html', {})
    if request.method == 'GET':
        customer, message_status = Customer.objects.get(id=pk), 0
        return render(request, 'app1/customer_detail.html', {'customer': customer})


@staff_member_required(login_url='/user/login')
def add_customer(request):       # error of form submition available in browser console
    if request.user and request.user.is_authenticated:
        if request.user.expiration_date and request.user.expiration_date < jdatetime.now():
            return render(request, 'app1/licence_time.html', {})
    message = ''
    if request.method == 'GET':
        try:
            return render(request, 'app1/add_customer.html', {'console': ''})
        except:
            return redirect('user:profile')

    elif request.method == 'POST':
        data = request.POST
        try:       # we just want fill dic_data with max possible for pre populating inputes when form refereshed
            pelak = Pelak.objects.get_or_create(number=data['pelak'])[0]
        except:
            pelak = None
        try:
            service = ServiceType.objects.get(id=data['service_type'])
        except:
            service = None
        try:
            center = Center.objects.get(id=data['service_center'])
        except:
            center = None
        try:
            state, town = State.objects.get(id=data['state']), Town.objects.get(id=data['town'])
        except Exception as e:
            state, town = None, None
        dic_data = {'username': data.get('username'), 'password': data.get('password'), 'phone': data.get('phone'), 'state': state, 'town': town, 'service_type': service, 'service_center': center, 'pelak': pelak, 'user': request.user, 'first_name': data.get('first_name'), 'last_name': data.get('last_name'), 'vehicle_cat': 'khodro'}
        try:
            customer = Customer.objects.create(**dic_data)
            message = '.کاربر با موفقیت ثبت شد'
            return render(request, 'app1/add_customer.html', {'customer': customer, 'message': message, 'console': ''})
        except Exception as e:
            message = '.اطلاعات وارد شده صحیح نمی باشد'
            return render(request, 'app1/add_customer.html', {'customer': dic_data, 'message': message, 'console': str(e)})


@staff_member_required(login_url='/user/login')
def edit_customer(request):       # error of form submition available in browser console
    if request.user and request.user.is_authenticated:
        if request.user.expiration_date and request.user.expiration_date < jdatetime.now():
            return render(request, 'app1/licence_time.html', {})
    message = ''
    try:
        customer = Customer.objects.get(id=request.GET.get('customer'))
    except:  # sometimes customer_id stale(lost) in query parameters
        return redirect('user:profile')
    current_state, current_town, current_service, current_center = StateSerializer(customer.state).data, TownSerializer(customer.town).data, ServiceTypeSerializer(customer.service_type).data, {'id': customer.service_center.id, 'name': customer.service_center.title}
    states, towns, services = StateSerializer(State.objects.all(), many=True).data, TownSerializer(customer.state.towns.all(), many=True).data, ServiceTypeSerializer(ServiceType.objects.all(), many=True).data
    vehicles = dict(VehicleCatChoices.choices)  # is like: {'khodro': 'نقلیه شخصی', ..}
    current_vehicle = {'id': customer.vehicle_cat, 'name': vehicles[customer.vehicle_cat]}  # is like {'khodro': 'نقلیه شخصی'}

    pre_pop_params = {'customer': customer, 'states': states, 'towns': towns, 'services': services, 'vehicles': vehicles, 'current_state': current_state, 'current_town': current_town, 'current_service': current_service, 'current_center': current_center, 'current_vehicle': current_vehicle}
    if request.method == 'GET':
        return render(request, 'app1/edit_customer.html', {**pre_pop_params})

    else:
        data = request.POST
        try:       # we just want fill dic_data with max possible for pre populating inputes when form refereshed
            pelak = Pelak.objects.get_or_create(number=data['pelak'])[0]
        except:
            pelak = None
        try:
            service = ServiceType.objects.get(id=data['service_type'])
        except:
            service = None
        try:
            center = Center.objects.get(id=data['service_center'])
        except:
            center = None
        try:
            state, town = State.objects.get(id=data['state']), Town.objects.get(id=data['town'])
        except Exception as e:
            state, town = None, None
        try:
            current_vehicle = {'id': data['vehicle_type'], 'name': vehicles[data['vehicle_type']]}
        except Exception as e:
            current_vehicle = None
        dic_data = {'username': data.get('username'), 'password': data.get('password'), 'phone': data.get('phone'), 'state': state, 'town': town, 'service_type': service, 'service_center': center, 'pelak': pelak, 'user': request.user, 'first_name': data.get('first_name', ''), 'last_name': data.get('last_name', ''), 'vehicle_cat': data.get('vehicle_type', '')}

        try:
            Customer.objects.filter(id=request.GET['customer']).update(**dic_data)
            message = '.کاربر با موفقیت ثبت شد'
            params = {**pre_pop_params, 'current_state': StateSerializer(state).data if state else None, 'current_town': TownSerializer(town).data if town else None, 'current_service': ServiceTypeSerializer(service).data if service else None, 'current_center': {'id': center.id, 'name': center.title} if center else None, 'current_vehicle': current_vehicle}
            return render(request, 'app1/edit_customer.html', {**params, 'message': message, 'console': ''})
        except Exception as e:
            message = '.اطلاعات وارد شده صحیح نمی باشد'
            params = {**pre_pop_params, 'current_state': StateSerializer(state).data if state else None, 'current_town': TownSerializer(town).data if town else None, 'current_service': ServiceTypeSerializer(service).data if service else None, 'current_center': {'id': center.id, 'name': center.title} if center else None, 'current_vehicle': current_vehicle}
            return render(request, 'app1/edit_customer.html', {**params, 'message': message, 'console': str(e)})



class NewCustomers(APIView):
    def get(self, request, *args, **kwargs):  # get all users to show in "متقاضی های ذخیره شده"
        data = []
        if request.user.is_authenticated and request.user.is_superuser:
            users = User.objects.prefetch_related('customers').all()
            for user in users:
                for customer in user.customers.exclude(status='complete'):
                    data.append(CustomerLinkSerializer(customer).data)
        elif request.user.is_authenticated and request.user.is_staff:
            data = list(CustomerLinkSerializer(request.user.customers.exclude(status='complete'), many=True).data)
        return Response({'customers': data})
