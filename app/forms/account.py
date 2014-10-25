from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms.models import formset_factory

from app.models.account import *


class SignUpUserForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_num', 'pickup_arrangements']

    def clean(self):
        cleaned_data = super(SignUpUserForm, self).clean()

        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError("Passwords do not match.")

        return self.cleaned_data


class SignUpAddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['apt_num', 'street', 'county', 'city', 'state', 'zip']


SignUpAddressFormSet = formset_factory(SignUpUserForm, SignUpAddressForm)


class SignInForm(AuthenticationForm):
    username = forms.EmailField()

    AuthenticationForm.error_messages['invalid_login'] = 'You may have entered a wrong email address or password.'
    AuthenticationForm.error_messages['inactive'] = 'Your ToolShare account has not been activated yet.'

    class Meta:
        model = User