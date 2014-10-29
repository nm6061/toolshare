from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms.models import formset_factory

from app.models.account import *


class SignUpUserForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput, required=True)

    def __init__(self, *args, **kwargs):
        super(SignUpUserForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.error_messages = {'required': 'Is required', 'invalid': 'is invalid'}

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
    def __init__(self, *args, **kwargs):
        super(SignUpAddressForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.error_messages = {'required': 'is required', 'invalid': 'is invalid'}

    class Meta:
        model = Address
        exclude = ['country']


SignUpAddressFormSet = formset_factory(SignUpUserForm, SignUpAddressForm)


class SignInForm(AuthenticationForm):
    username = forms.EmailField()

    AuthenticationForm.error_messages['invalid_login'] = 'You may have entered a wrong email address or password.'
    AuthenticationForm.error_messages['inactive'] = 'Your ToolShare account has not been activated yet.'

    def __init__(self, *args, **kwargs):
        super(SignInForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.error_messages = {'required': 'is required', 'invalid': 'is invalid'}

    class Meta:
        model = User