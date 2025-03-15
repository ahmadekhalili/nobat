from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.utils.translation import gettext_lazy as _

from .models import Customer, User, Pelak
from .forms import AccountUserChangeForm


class AcountUserAdmin(UserAdmin):
    form = AccountUserChangeForm
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'expiration_date')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined')
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Modify the help text of the 'expiration_date' field
        form.base_fields['expiration_date'].help_text = "Field format: 18d 00:00:00 or 18d"
        return form
admin.site.register(User, AcountUserAdmin)





class CustomerUserAdmin(admin.ModelAdmin):
    change_form_template = "admin/user/customer/change_form.html"
    # Using the default form, so no extra ModelForm is needed
    css = {
        'all': ('admin/css/rtl_sup..css',)  # Path relative to your static files
    }
    exclude = (
        'time1', 'time2', 'time3', 'time4',
        'date1', 'date2', 'date3', 'date4',
    )
admin.site.register(Customer, CustomerUserAdmin)


class PelakAdmin(admin.ModelAdmin):
    # Using the default form, so no extra ModelForm is needed
    css = {
        'all': ('admin/css/rtl_sup..css',)  # Path relative to your static files
    }
admin.site.register(Pelak, PelakAdmin)
