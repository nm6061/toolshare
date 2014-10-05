from app.constants import Constants
from app import models
from django import forms
from django.contrib.auth.forms import AuthenticationForm


class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, required=True)

    states = forms.ChoiceField(choices=Constants.US_STATES)

    class Meta:
        model = models.User
        fields = ['first_name', 'last_name', 'email', 'phone_num', 'pickup_arrangements', 'apt_num', 'street',
                  'county', 'city', 'zip']

    def clean(self):
        cleaned_data = super(SignUpForm, self).clean()

        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError("Passwords do not match.")

        return self.cleaned_data

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.state = self.cleaned_data['states']

        if commit:
            user.save()

        return user


class SignInForm(AuthenticationForm):
    # TODO : Figure out how to get username to be rendered as an input of type=email
    AuthenticationForm.error_messages['invalid_login'] = "Invalid login"

    class Meta:
        model = models.User