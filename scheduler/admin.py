from django.contrib import admin
from .models import Job, CrawlFuncArgs

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    readonly_fields = ('start_time',)
    #list_display = ('id', 'start_date', 'end_date', 'customer_id')  # Columns in admin list
    #search_fields = ('customer_id')  # Enables search box
    list_filter = ('status',)  # Adds a sidebar filter
    ordering = ('-start_time',)  # Orders by newest jobs first


admin.site.register(CrawlFuncArgs)
