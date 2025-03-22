from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from django_jalali.db import models as jmodels
from phonenumber_field.modelfields import PhoneNumberField
import re


def validate_national_code(value):
    """
    Validator to ensure the national code is exactly 10 digits.
    """
    if not re.fullmatch(r'\d{10}', value):
        raise ValidationError("National code must be exactly 10 digits.")


def pelak_validator(value):  # for next implementation (motors, varedati.. and other are so be care)!
    if not re.fullmatch(r'^\d{2}[A-Za-z\u0600-\u06FF]\d{5}$', value):  # accept unicode cahrs in addition of english in:  [A-Za-z\u0600-\u06FF]
        raise ValidationError('Pelak must be in the format ddCddddd (2 digits, 1 letter, 5 digits).')


class State(models.Model):
    name = models.CharField(max_length=150, verbose_name=_('name'))
    # towns

    class Meta:
        verbose_name = _('State')
        verbose_name_plural = _('States')

    def __str__(self):
        return self.name


class Town(models.Model):
    name = models.CharField(max_length=150, verbose_name=_('name'))
    state = models.ForeignKey(State, related_name='towns', on_delete=models.SET_NULL, null=True, verbose_name=_('state'))

    class Meta:
        verbose_name = _('Town')
        verbose_name_plural = _('Towns')

    def __str__(self):
        return self.name


class User(AbstractUser):
    # customers
    expiration_date = jmodels.jDateTimeField(null=True, blank=True, help_text="Jalali datetime field for remain time of user")
    phone = PhoneNumberField(null=True, blank=True, unique=True)
    active_code = models.CharField(max_length=255, blank=True, default="")
    # Override the username field with a custom validator
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[validate_national_code],
        help_text="National code must be exactly 10 digits.",
        error_messages={
            'unique': "A user with that national code already exists.",
        },
    )

    # Optional: if you want to ensure validation at the model level too,
    # you can override the clean() method.
    def clean(self):
        super().clean()
        validate_national_code(self.username)


# PELAK_LETTER_OPTIONS used by crawl.py
PELAK_LETTER_OPTIONS = {"ق": "10", "ل": "11", "م": "12", "ن": "13", "و": "14", "ه": "15", "ي": "16", "ر": "17", "♿": "19", "ب": "02", "ج": "04", "د": "05", "س": "06", "ص": "07", "ط": "08"}
class Pelak(models.Model):
    number = models.CharField(max_length=20, blank=False)
    letter_value = models.CharField(max_length=20, blank=True)  # <option value=..> in the site, for example for letter 'ق' value is: '10'

    def __str__(self):
        return f'Pelak ({self.id}) - {self.number}'


    def save(self, *args, **kwargs):
        # Automatically set letter_value based on the letter field
        if self.number[2].isalpha():  # is not 'motor' format pelak
            self.letter_value = PELAK_LETTER_OPTIONS[self.number[2]]
        super().save(*args, **kwargs)

class ServiceType(models.Model):
    name = models.CharField(max_length=150, null=False, blank=False)

    def __str__(self):
        return self.name


class Center(models.Model):
    towns = models.ManyToManyField(Town)
    services = models.ManyToManyField(ServiceType)

    title = models.CharField(max_length=255, null=False, blank=False)
    address = models.TextField(null=False, blank=False)
    code = models.CharField(max_length=255, null=False, blank=True)
    active = models.BooleanField(default=True)    # centers without code are inactive

    def __str__(self):
        return self.title


class VehicleCatChoices(models.TextChoices):
    CHOOSE = '', '-- انتخاب کنید'
    KHUDRO = 'khodro', 'سواری شخصی'
    KHUDRO_DOLATI = 'khodro_dolati', 'سواری دولتی'
    VANET = 'vanet', 'وانت شخصی'
    VANET_DOULATI = 'vanet_doulati', 'وانت دولتی'
    MOTOR = 'motor', 'موتور سیکلت'
    TAXI = 'taxi', 'تاکسی'


class Customer(models.Model):
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[validate_national_code],
        help_text="National code must be exactly 10 digits.",
        error_messages={
            'unique': "A user with that national code already exists.",
        },
    )
    password = models.CharField(max_length=150, null=False, blank=False)
    phone = PhoneNumberField(blank=False, unique=True)
    vehicle_cat = models.CharField(max_length=150, choices=VehicleCatChoices.choices, default=VehicleCatChoices.CHOOSE,)  # note: costomer.vehicle_cat returns like: 'khodro' if you want persian type use: customer.get_vehicle_cat_display() == 'سواری شخصی'
    cd_peigiri = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=30, default="stop")       # start/stop/complete/unknown
    result_image = models.ImageField(upload_to='result_images/', blank=True)
    color_classes = models.TextField(blank=True)  # how much crawling browser are running for this user
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    finall_message = models.CharField(max_length=255, blank=True, default="")

    customer_time = models.CharField(max_length=30, blank=True)  # reservation time
    customer_date = models.CharField(max_length=30, blank=True)
    time1 = models.CharField(max_length=30, blank=True)  # start crawling times
    time2 = models.CharField(max_length=30, blank=True)
    time3 = models.CharField(max_length=30, blank=True)
    time4 = models.CharField(max_length=30, blank=True)
    date1 = models.CharField(max_length=30, blank=True)  # start crawling dates
    date2 = models.CharField(max_length=30, blank=True)
    date3 = models.CharField(max_length=30, blank=True)
    date4 = models.CharField(max_length=30, blank=True)

    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, related_name='customers', related_query_name='customer')
    town = models.ForeignKey(Town, on_delete=models.SET_NULL, null=True, related_name='customers', related_query_name='customer')
    pelak = models.ForeignKey(Pelak, on_delete=models.SET_NULL, null=True, related_name='customers', related_query_name='customer')  # user in several models like user and customer ...
    service_type = models.ForeignKey(ServiceType, on_delete=models.SET_NULL, null=True, blank=False, related_name='customers', related_query_name='customer')
    service_center = models.ForeignKey(Center, on_delete=models.SET_NULL, null=True, related_name='customers', related_query_name='customer')     # markaze khadmat like 'alghadir'
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customers', related_query_name='customer')

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name} - {self.username}"
        return f"کاربر - {self.username}"

