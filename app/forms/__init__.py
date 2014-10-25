from app import models
from django import forms
from django.contrib.auth.forms import AuthenticationForm


class addToolForm(forms.ModelForm):
    class Meta:
        model = models.Tool
        fields = ['name', 'description', 'category', 'location', 'picture', 'pickupArrangement']
        widgets = {
            'location': forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        super(addToolForm, self).__init__(*args, **kwargs)

        self.fields['name'].error_messages = {'required': 'Please enter a name for the tool.'}
        self.fields['description'].error_messages = {'required': 'Please provide a description of your tool.'}
        self.fields['category'].error_messages = {'required': 'Please choose which category your tool falls into.'}
        self.fields['location'].error_messages = {'required': 'Please choose where your tool will be shared from.'}
        self.fields['picture'].error_messages = {'required': 'Please upload a picture of the tool.'}
        self.fields['pickupArrangement'].error_messages = {'required': 'Please specify a pickup arrangement.'}

    def clean_name(self):
        return self.cleaned_data['name'].strip().capitalize()

    def clean_description(self):
        return self.cleaned_data['description'].strip().capitalize()

    def clean_pickupArrangement(self):
        return self.cleaned_data['pickupArrangement'].strip().capitalize()


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ['first_name', 'last_name', 'phone_num', 'email', 'pickup_arrangements']


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
