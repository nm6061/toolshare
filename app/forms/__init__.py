from django import forms

from app import models
from app.models.reservation import Reservation


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ['first_name', 'last_name', 'phone_num', 'email', 'pickup_arrangements']


class ApproveReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        Fields = ['from_date', 'to_date', 'tool', 'reservedBy']

    def clean(self):
        return self.cleaned_data

class RejectReservationForm(forms.ModelForm):
    class Meta:
        model = models.Reservation
        Fields = ['message']

    def clean(self):
        return self.cleaned_data        



class BorrowToolForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['from_date', 'to_date']
    def __init__(self, *args, **kwargs):
        super(BorrowToolForm, self).__init__(*args, **kwargs)

        self.fields['from_date'].error_messages = {'required': 'Please enter a date for the tool.'}
        self.fields['to_date'].error_messages = {'required': 'Please enter a date for the tool.'}

    def clean(self):
        cleaned_data = super(BorrowToolForm, self).clean()

        if 'from_date' in self.cleaned_data and 'to_date' in self.cleaned_data:
            if self.cleaned_data['from_date'] >= self.cleaned_data['to_date']:
                raise forms.ValidationError("From Date should be before To date")

        return self.cleaned_data

