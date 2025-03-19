from django.urls import path

from . import views

app_name = 'user'

urlpatterns = [
    path('', views.profile, name='profile'),
    path('login/', views.login_account, name='login'),
    path('login2/', views.login_account2, name='login2'),
    path('logout/', views.logout_account, name='logout'),  # menu 6
    path('<pk>/activate/', views.activate, name='activate'),
    path('customers/', views.reserved_customers, name='reserved_customers_list'),  # menu 2
    path('<pk>/customer/', views.customer_detail, name='customer'),
    path('add/', views.add_customer, name='add-customer'),  # menu 3
    path('edit/', views.edit_customer, name='edit-customer'),  # menu 5
    path('api/new_customers_list/', views.NewCustomers.as_view(), name='new_customers_list'),
]
