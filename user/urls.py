from django.urls import path

from . import views

app_name = 'user'

urlpatterns = [
    path('', views.profile, name='profile'),
    path('login/', views.login_account, name='login'),
    path('login2/', views.login_account2, name='login2'),
    path('logout/', views.logout_account, name='logout'),
    path('<pk>/activate/', views.activate, name='activate'),
    path('customers/', views.customers_list, name='customers-list'),
    path('<pk>/customer/', views.customer_detail, name='customer'),
    path('add/', views.add_customer, name='add-customer'),
    path('edit/', views.edit_customer, name='edit-customer'),
    path('api/all_users_json/', views.all_users_json.as_view(), name='all_users_json'),
]
