from app import models
from django import forms
from django.contrib.auth.forms import AuthenticationForm


class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = models.User
        fields = ['first_name', 'last_name', 'email', 'phone_num', 'pickup_arrangements', 'apt_num', 'street',
                  'county', 'city', 'state', 'zip']

    def clean(self):
        cleaned_data = super(SignUpForm, self).clean()

        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError("Passwords do not match.")

        return self.cleaned_data

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])

        # ShareZone creation

        # ShareZone.zip is 9 characters wide for flexibility
        zip = (user.zip[:5]).ljust(9, '0')
        share_zone = models.System.get_or_create_share_zone(zip)

        if share_zone == None:
            share_zone = models.ShareZone()
            share_zone.zip = zip
            share_zone.save()

        user.share_zone = share_zone

        if commit:
            user.save()

        return user


class SignInForm(AuthenticationForm):
    # TODO : Figure out how to get username to be rendered as an input of type=email
    AuthenticationForm.error_messages['invalid_login'] = "Invalid login"

    class Meta:
        model = models.User


class addToolForm(forms.ModelForm):
    class Meta:
        model = models.Tool
        fields = ['name', 'description', 'category', 'location', 'picture']


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ['first_name', 'last_name', 'apt_num', 'street', 'county', 'city', 'state', 'zip', 'phone_num',
                  'email', 'pickup_arrangements']


class ApproveReservationForm(forms.ModelForm):
    class Meta:
        model = models.Reservation
        Fields = ['from_date', 'to_date', 'tool', 'reservedBy']

    def clean(self):
        return self.cleaned_data


class BorrowToolForm(forms.ModelForm):
    class Meta:
        model = models.Reservation
        fields = ['from_date', 'to_date']
