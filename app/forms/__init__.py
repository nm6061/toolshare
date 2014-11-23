import datetime, json
from django import forms

from app.models.reservation import Reservation
from app.models import BlackoutDate


class ApproveReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        Fields = ['from_date', 'to_date', 'tool', 'reservedBy']

    def clean(self):
        return self.cleaned_data


class RejectReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        Fields = ['message']

    def clean(self):
        return self.cleaned_data


class BorrowToolForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['from_date', 'to_date']


    def __init__(self, tool, user, *args, **kwargs):
        super(BorrowToolForm, self).__init__(*args, **kwargs)
        self.tool = tool
        self.user = user

        for field in self.fields.values():
            field.error_messages = {'required': 'is required'}

    def clean_from_date(self):
        from_date = self.cleaned_data['from_date']

        if from_date < datetime.date.today():
            raise forms.ValidationError('cannot be earlier than today.')

        if 'to_date' in self.cleaned_data:
            to_date = self.cleaned_data['to_date']
            if from_date > to_date:
                raise forms.ValidationError('cannot be earlier than ' + self.fields['to_date'].auto_id)

        return from_date

    def clean_to_date(self):
        to_date = self.cleaned_data['to_date']

        if to_date < datetime.date.today():
            raise forms.ValidationError('cannot be earlier than today.')

        return to_date

    def clean(self):
        super(BorrowToolForm, self).clean()

        if 'from_date' in self.cleaned_data and 'to_date' in self.cleaned_data:
            fd = self.cleaned_data['from_date']
            td = self.cleaned_data['to_date']

            if fd > td:
                self._errors['to_date'] = self.error_class(' cannot be earlier than from date')

            for ud in self.get_unavailable_dates():
                if not (fd > ud['end'] or td < ud['start']):
                    raise forms.ValidationError('The tool is not available on the dates selected.')

        return self.cleaned_data

    def save(self, commit=True):
        data = {
            'from_date': self.cleaned_data['from_date'],
            'to_date': self.cleaned_data['to_date'],
            'status': 'Pending',
            'tool': self.tool,
            'user': self.user
        }

        reservation = Reservation.objects.create(**data)
        reservation.save()

    def get_unavailable_dates(self):
        unavailable_dates = []

        # Tool is unavailable when during its blackout dates
        unavailable_dates = unavailable_dates + [{'start': bd.blackoutStart, 'end': bd.blackoutEnd} for bd in
                                                 self.tool.blackoutdate_set.all()]

        # Tool is considered unavailable for dates that it has an approved reservation
        unavailable_dates = unavailable_dates + [{'start': r.from_date, 'end': r.to_date} for r in
                                                 self.tool.reservation_set.filter(status='Approved')]

        # Tool is considered unavailable for dates that the user has requested to borrow the tool irrespective of the
        # status of the reservation
        unavailable_dates = unavailable_dates + [{'start': r.from_date, 'end': r.to_date} for r in
                                                 self.tool.reservation_set.filter(user=self.user)]

        return unavailable_dates

    @property
    def unavailable_dates(self):
        return json.dumps(self.get_unavailable_dates(), cls=JSONDateEncoder)


class JSONDateEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, 'isoformat'):
            o = datetime.datetime.strptime(o.isoformat(),'%Y-%m-%d')
            return o.isoformat()