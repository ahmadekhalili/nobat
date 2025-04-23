from django.urls import path

from . import views

app_name = 'main'

urlpatterns = [
    path('index/', views.index, name='index'),
    path('celery/', views.test_celery.as_view(), name='test_celery'),
    path('states/', views.States.as_view(), name='states'),
    path('towns_by_state/', views.TownByState.as_view(), name='towns-by-state'),
    path('service_list/', views.ServiceList.as_view(), name='service_list'),
    path('selected_centers/', views.CentersByTownService.as_view(), name='selected_centers'),
    path('crawl/', views.CrawlCustomer.as_view(), name='crawl_customer'),
    path('stop_crawl/', views.StopCrawl.as_view(), name='stop_crawl'),
    path('licence_time/', views.licence, name='licence-time'),    # menu 4
    path('square_nums/', views.StartButtonSquares.as_view(), name='square_nums'),
    path('test/', views.test.as_view(), name='test'),
    path('browser_list/', views.BrowserIconList.as_view(), name='browser_list'),
    path('browser_close/', views.CloseBrowsers.as_view(), name='browser_status'),
    path('browser_status/', views.BrowserStatus.as_view(), name='browser_status'),

]
