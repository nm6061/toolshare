from app import models
from app.constants import Constants
from django.forms import ModelForm, ChoiceField
from django.contrib.auth.forms import UserCreationForm


class SignUpUserForm(UserCreationForm):
    class Meta:
        model = models.User
        fields = ['first_name', 'last_name', 'email', 'phone_num', 'pickup_arrangements']


class SignUpAddressForm(ModelForm):
    states = ChoiceField(choices=Constants.US_STATES)

    class Meta:
        model = models.Address
