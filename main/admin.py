from django.contrib import admin

from user.models import Center, State, Town
from .models import *

class CenterAdmin(admin.ModelAdmin):
    list_display = ('title', 'display_towns', 'code', 'active')
    list_filter = ('towns',)  # Enables filtering by towns
    search_fields = ('title',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Prefetch related towns to optimize queries
        return qs.prefetch_related('towns')  # enable search on the title field

    def display_towns(self, obj):
        # Join town names with a comma separator
        return ", ".join([town.name for town in obj.towns.all()])
    display_towns.short_description = 'Towns'  # Column header in admin

admin.site.register(Center, CenterAdmin)
#admin.site.register(ServiceType)
admin.site.register(State)
admin.site.register(Town)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    readonly_fields = ('start_time',)
    #list_display = ('id', 'start_date', 'end_date', 'customer_id')  # Columns in admin list
    #search_fields = ('customer_id')  # Enables search box
    #list_filter = ('is_test',)  # Adds a sidebar filter
    ordering = ('-start_time',)  # Orders by newest jobs first


admin.site.register(CrawlFuncArgs)
