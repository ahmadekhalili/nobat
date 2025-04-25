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
    path('browser_minimize/', views.BrowserMinimize.as_view(), name='browser_minimize'),
    path('browser_open/', views.BrowserOpen.as_view(), name='browser_open'),
    path('kill_process/', views.KillProcess.as_view(), name='kill_process'),
    path('stop_job/', views.StopJob.as_view(), name='stop_job'),
    path('repeat_job/', views.ReapeatJob.as_view(), name='repeat_job'),

]
