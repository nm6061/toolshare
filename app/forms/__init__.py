import datetime, json
from django import forms, conf
from pytz import timezone

from app.models.reservation import *
from app.models.tool import *

server_timezone = timezone(conf.settings.TIME_ZONE)


class RejectReservationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(RejectReservationForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.error_messages = {'required': 'is required', 'invalid': 'is invalid'}

        # Hack Alert: Message field is not required by default
        self.fields['message'].required = True

    class Meta:
        model = Reservation
        fields = ['message']

    def save(self, commit=True):
        self.instance.status = 'R'
        return super(RejectReservationForm, self).save(commit)


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
        status = 'P'
        if self.tool.location == 'S':
            status = 'A'

        data = {
            'from_date': self.cleaned_data['from_date'],
            'to_date': self.cleaned_data['to_date'],
            'status': status,
            'tool': self.tool,
            'user': self.user
        }

        reservation = Reservation.objects.create(**data)
        reservation.save()

        return reservation

    def get_unavailable_dates(self):
        ud = []

        # Tool is unavailable when during its blackout dates
        ud = ud + [{'start': bd.blackoutStart, 'end': bd.blackoutEnd} for bd in self.tool.blackoutdate_set.filter(
            blackoutEnd__gte=datetime.date.today())]

        # Tool is considered unavailable for dates that it has an approved reservation
        ud = ud + [{'start': r.from_date, 'end': r.to_date} for r in
                   self.tool.reservation_set.filter(status='A', to_date__gte=datetime.date.today())]

        # Tool is considered unavailable for dates that it has an active reservation
        ud = ud + [{'start': r.from_date, 'end': r.to_date} for r in
                   self.tool.reservation_set.filter(status='AC')]

        # Tool is considered unavailable for dates that it has a return initiated reservation
        ud = ud + [{'start': r.from_date, 'end': r.to_date} for r in
                   self.tool.reservation_set.filter(status='RI')]

        # Tool is unavailable for dates where the borrower has a pending borrow request on the tool
        ud = ud + [{'start': r.from_date, 'end': r.to_date} for r in
                   self.tool.reservation_set.filter(user=self.user, status='P')]

        return ud

    @property
    def unavailable_dates(self):
        return json.dumps(self.get_unavailable_dates(), cls=JSONDateEncoder)


class BlackoutDateForm(forms.ModelForm):
    class Meta:
        model = BlackoutDate
        fields = ['blackoutStart', 'blackoutEnd']


    def __init__(self, tool, *args, **kwargs):
        super(BlackoutDateForm, self).__init__(*args, **kwargs)
        self.tool = tool
        for field in self.fields.values():
            field.error_messages = {'required': 'is required'}

    def clean_blackoutStart(self):
        blackoutStart = self.cleaned_data['blackoutStart']

        if blackoutStart < datetime.date.today():
            raise forms.ValidationError('cannot be earlier than today.')

        if 'blackoutEnd' in self.cleaned_data:
            blackoutEnd = self.cleaned_data['blackoutEnd']
            if blackoutStart > blackoutEnd:
                raise forms.ValidationError('cannot be earlier than ' + self.fields['blackoutEnd'].auto_id)
        return blackoutStart

    def clean_blackoutEnd(self):
        blackoutEnd = self.cleaned_data['blackoutEnd']

        if blackoutEnd < datetime.date.today():
            raise forms.ValidationError('cannot be earlier than today.')

        return blackoutEnd

    def clean(self):
        super(BlackoutDateForm, self).clean()

        if 'blackoutStart' in self.cleaned_data and 'blackoutEnd' in self.cleaned_data:
            fd = self.cleaned_data['blackoutStart']
            td = self.cleaned_data['blackoutEnd']

            if fd > td:
                self._errors['blackoutEnd'] = self.error_class(' cannot be earlier than from date')

            for ud in self.get_unavailable_dates():
                if not (fd > ud['end'] or td < ud['start']):
                    raise forms.ValidationError('Chosen dates conflict with existing reservations or blackouts.')

        return self.cleaned_data

    def save(self, commit=True):
        data = {
            'blackoutStart': self.cleaned_data['blackoutStart'],
            'blackoutEnd': self.cleaned_data['blackoutEnd'],
            'tool': self.tool,
        }

        blackout = BlackoutDate.objects.create(**data)
        blackout.save()

        return blackout

    def get_unavailable_dates(self):
        unavailable_dates = []

        # Cannot be blacked out during existing blackout days
        unavailable_dates = unavailable_dates + [{'start': bd.blackoutStart, 'end': bd.blackoutEnd} for bd in
                                                 self.tool.blackoutdate_set.all()]

        # Cannot be blacked out on dates with approved reservations
        unavailable_dates = unavailable_dates + [{'start': r.from_date, 'end': r.to_date} for r in
                                                 self.tool.reservation_set.filter(status='A')]

        # Cannot be blacked out on dates with pending reservations
        unavailable_dates = unavailable_dates + [{'start': r.from_date, 'end': r.to_date} for r in
                                                 self.tool.reservation_set.filter(status='P')]

        # Cannot be blacked out on dates with active reservations
        unavailable_dates = unavailable_dates + [{'start': r.from_date, 'end': r.to_date} for r in
                                                 self.tool.reservation_set.filter(status='AC')]

        # Cannot be blacked out on dates with return initiated reservations
        unavailable_dates = unavailable_dates + [{'start': r.from_date, 'end': r.to_date} for r in
                                                 self.tool.reservation_set.filter(status='RI')]

        return unavailable_dates

    @property
    def unavailable_dates(self):
        return json.dumps(self.get_unavailable_dates(), cls=JSONDateEncoder)


class JSONDateEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, 'isoformat'):
            o = server_timezone.localize(datetime.datetime.strptime(o.isoformat(), '%Y-%m-%d'))
            return o.isoformat()