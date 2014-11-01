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
                raise forms.ValidationError('Passwords do not match.', code='distinct_pass')

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


class RecoverAccountForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(RecoverAccountForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.error_messages = {'required': 'is required', 'invalid': 'is invalid'}

    class Meta:
        model = User
        fields = ['email']

    def clean(self):
        email = self.cleaned_data.get('email')

        if email:
            try:
                user = User.objects.get(email=email)
                if not user.is_active:
                    raise forms.ValidationError(
                        'You cannot reset the password on an account that has not been activated yet.', code='inactive')
                    return user
            except User.DoesNotExist:
                raise forms.ValidationError(
                    'There is no account matching the email address you entered.', code='not_found')

        return self.cleaned_data

    def save(self, site, user, uidb64, token):
        template_name = 'email/account_reset.html'
        email = self.cleaned_data['email']

        user = User.objects.get(email=email)

        context = {
            'site': site,
            'user': user,
            'uidb64': uidb64,
            'token': token
        }
        subject = 'ToolShare Account Password Reset'
        message = render_to_string(template_name, context)

        user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)


class ResetAccountForm(forms.Form):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label='Confirm', widget=forms.PasswordInput, required=True)

    def __init__(self, *args, **kwargs):
        super(ResetAccountForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.error_messages = {'required': 'Is required', 'invalid': 'is invalid'}

    def clean(self):
        cleaned_data = super(ResetAccountForm, self).clean()

        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError('Passwords do not match.', code='distinct_pass')

        return self.cleaned_data

    def save(self, user):
        raw_password = self.cleaned_data['password1']
        user.set_password(raw_password)
        user.save()