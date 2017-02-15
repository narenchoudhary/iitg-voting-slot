from django import forms
from django.core.exceptions import ValidationError
from django.db.models import F
from django.utils.translation import ugettext as _

from constants import LOGIN_SERVER
from models import Appointment, Slot


class LoginForm(forms.Form):
    username = forms.CharField(required=True, label='webmail')
    password = forms.CharField(required=True, widget=forms.PasswordInput)
    login_server = forms.ChoiceField(required=True, choices=LOGIN_SERVER)

    def clean_login_server(self):
        valid_servers = ['202.141.80.9', '202.141.80.10', '202.141.80.11',
                         '202.141.80.12', '202.141.80.13']
        login_server = self.cleaned_data.get('login_server')
        if login_server not in valid_servers:
            raise ValidationError(_('Invalid Login Server'), code='invalid')
        return login_server


class TokenForm(forms.ModelForm):

    class Meta:
        model = Appointment
        fields = ['slot']

    def __init__(self, *args, **kwargs):
        super(TokenForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['slot'].queryset = Slot.objects.filter(
                stud_count__lt=F('max_limit')
            ).order_by('start_time')
            self.fields['slot'].label = 'Select a slot from dropdown'

    def clean_slot(self):
        slot = self.cleaned_data.get('slot', None)
        if slot is None:
            raise ValidationError(_("Please select a slot"))
        if slot.stud_count > slot.max_limit:
            raise ValidationError(_(
                "This slot is already filled. Select another slot."
            ))
        return slot
