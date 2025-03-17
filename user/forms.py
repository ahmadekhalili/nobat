# user/forms.py
from django.contrib.auth.forms import UserChangeForm
from user.models import User
from .widgets import RemainingTimeWidget

from django_jalali.forms import jDateTimeField


class AccountUserChangeForm(UserChangeForm):
    #expiration_date = jDateTimeField(widget=RemainingTimeWidget(), help_text="Field format: 18d 00:23:22")  # Explicitly set the form field

    class Meta:
        model = User
        fields = '__all__'
        widgets = {'expiration_date': RemainingTimeWidget()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update help texts as needed.
        self.fields['username'].help_text = 'You have to add 10 digit "cd meli"'
        self.fields['password'].help_text = (
            'You can change the password using <a href="../../1/password/">this form</a>.'
        )
