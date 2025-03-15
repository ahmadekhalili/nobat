from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.admin.views.decorators import staff_member_required

from rest_framework.views import APIView
from rest_framework.response import Response

from .models import *
from .methods import generate_activation_code
from .serializers import *


def login_account(request):
    user, message, message_status = object(), "", 0
    if request.method == 'GET':
        return render(request, 'app1/login.html', {'message': message, 'message_status': message_status})

    elif request.method == 'POST':
        data = request.POST
        user = authenticate(request, username=data['cdmeli'], password=data['password'])
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


def logout_account(request):
    if request.method == 'GET':
        logout(request)
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


@staff_member_required(login_url='/user/login')
def profile(request):
    time_slots = [f"{hour:02d}:{minute:02d}" for hour in range(7, 17) for minute in range(0, 60, 10) if not (hour == 16 and minute > 0)]

    if request.method == 'GET':  # 'user' auto fills in templates if user logged in
        message_status = 0
        if request.GET.get('customer'):
            customer = Customer.objects.get(id=request.GET['customer'])
            customer.status = 'stop'  # could changes in CrawlCustomer.post, so should reset here
            customer.save()
        else:
            customer = None
        return render(request, 'app1/profile_page.html', {'customer': customer, 'time_slots': time_slots})


@staff_member_required(login_url='/user/login')
def customers_list(request):
    if request.method == 'GET':
        customers = request.user.customers.all()
        return render(request, 'app1/customer_list.html', {'customers': customers})


@staff_member_required(login_url='/user/login')
def customer_detail(request, pk):
    if request.method == 'GET':
        customer, message_status = Customer.objects.get(id=pk), 0
        return render(request, 'app1/customer_detail.html', {'customer': customer})


@staff_member_required(login_url='/user/login')
def add_customer(request):       # error of form submition available in browser console
    message = ''
    if request.method == 'GET':
        return render(request, 'app1/add_customer.html', {'console': ''})

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
        dic_data = {'username': data.get('username'), 'password': data.get('password'), 'phone': data.get('phone'), 'state': state, 'town': town, 'service_type': service, 'service_center': center, 'pelak': pelak, 'user': request.user, 'first_name': data.get('first_name'), 'last_name': data.get('last_name')}
        try:
            customer = Customer.objects.create(**dic_data)
            message = '.کاربر با موفقیت ثبت شد'
            return render(request, 'app1/add_customer.html', {'customer': customer, 'message': message, 'console': ''})
        except Exception as e:
            message = '.اطلاعات وارد شده صحیح نمی باشد'
            return render(request, 'app1/add_customer.html', {'customer': dic_data, 'message': message, 'console': str(e)})


@staff_member_required(login_url='/user/login')
def edit_customer(request):       # error of form submition available in browser console
    message = ''
    customer = Customer.objects.get(id=request.GET['customer'])
    current_state, current_town, current_service, current_center = StateSerializer(customer.state).data, TownSerializer(customer.town).data, ServiceTypeSerializer(customer.service_type).data, {'id': customer.service_center.id, 'name': customer.service_center.title}
    states, towns, services = StateSerializer(State.objects.all(), many=True).data, TownSerializer(customer.state.towns.all(), many=True).data, ServiceTypeSerializer(ServiceType.objects.all(), many=True).data

    pre_pop_params = {'customer': customer, 'states': states, 'towns': towns, 'services': services, 'current_state': current_state, 'current_town': current_town, 'current_service': current_service, 'current_center': current_center}
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
        dic_data = {'username': data.get('username'), 'password': data.get('password'), 'phone': data.get('phone'), 'state': state, 'town': town, 'service_type': service, 'service_center': center, 'pelak': pelak, 'user': request.user, 'first_name': data.get('first_name', ''), 'last_name': data.get('last_name', '')}
        try:
            Customer.objects.filter(id=request.GET['customer']).update(**dic_data)
            message = '.کاربر با موفقیت ثبت شد'
            params = {**pre_pop_params, 'current_state': StateSerializer(state).data if state else None, 'current_town': TownSerializer(town).data if town else None, 'current_service': ServiceTypeSerializer(service).data if service else None, 'current_center': {'id': center.id, 'name': center.title} if center else None}
            return render(request, 'app1/add_customer.html', {**params, 'message': message, 'console': ''})
        except Exception as e:
            message = '.اطلاعات وارد شده صحیح نمی باشد'
            params = {**pre_pop_params, 'current_state': StateSerializer(state).data if state else None, 'current_town': TownSerializer(town).data if town else None, 'current_service': ServiceTypeSerializer(service).data if service else None, 'current_center': {'id': center.id, 'name': center.title} if center else None}
            return render(request, 'app1/add_customer.html', {**params, 'message': message, 'console': str(e)})



class all_users_json(APIView):
    def get(self, request, *args, **kwargs):
        # Use prefetch_related to optimize fetching of related customers
        users = User.objects.prefetch_related('customers').all()
        data = []
        for user in users:
            for customer in user.customers.all():
                # Prepare display name based on available customer data
                if customer.first_name and customer.last_name:
                    display_name = f"{customer.first_name} {customer.last_name} - {customer.username}"
                else:
                    display_name = f"کاربر - {customer.username}"
                data.append({
                    'id': customer.id,
                    'display_name': display_name,
                })
        return Response({'customers': data})