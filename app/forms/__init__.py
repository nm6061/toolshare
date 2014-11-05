from django import forms

from app import models
from app.models.reservation import Reservation
import datetime
from app.models import BlackoutDate
import pdb;


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
        #for field in self.fields.values():
         #   field.error_messages = {'required': 'Is required', 'invalid': 'is invalid'}

        self.fields['from_date'].error_messages = {'required': 'Please enter a date for the tool.'}
        self.fields['to_date'].error_messages = {'required': 'Please enter a date for the tool.'}




    def clean(self):
        today = datetime.date.today()
        #pdb.set_trace()
        cleaned_data = super(BorrowToolForm, self).clean()
        blackoutStart='11/11/1991'
        blackoutEnd='12/12/1991'

        if 'from_date' in self.cleaned_data and 'to_date' in self.cleaned_data:
            if self.cleaned_data['from_date'] <=today and self.cleaned_data['to_date']<=today   :
                raise forms.ValidationError("can't book past dates")

        if 'from_date' in self.cleaned_data and 'to_date' in self.cleaned_data:
            if self.cleaned_data['from_date'] >= self.cleaned_data['to_date'] :
                raise forms.ValidationError("From Date should be before To date")

        #if 'from_date' in self.cleaned_data :
         #   if self.cleaned_data['from_date'] >=BlackoutDate.objects.get(blackoutStart=blackoutStart)  and self.cleaned_data['from_date'] <= BlackoutDate.objects.get(blackoutEnd=blackoutEnd) :
          #      raise forms.ValidationError("From Date must avoid blackout dates")

        #if 'to_date' in self.cleaned_data  :
         #  if self.cleaned_data['to_date'] >= BlackoutDate.objects.get(blackoutStart=blackoutStart) and self.cleaned_data['to_date'] <= BlackoutDate.objects.get(blackoutEnd=blackoutEnd):
          #   raise forms.ValidationError("To Date must avoid blackout dates")

        return self.cleaned_data

