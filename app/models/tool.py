from django.conf import settings
from django.db import models
from imagekit.models import ProcessedImageField
from pilkit.processors import Resize
from app.models.shed import Shed
import app.constants
import datetime


class Tool(models.Model):
    class Meta:
        app_label = 'app'

    def toolPictureName(instance, filename):
        ext = filename.split('.')[-1]
        return 'toolpics/{}.{}'.format(instance.name, ext)

    name = models.CharField(max_length=25)
    picture = ProcessedImageField(processors=[Resize(500, 500)], format='JPEG', upload_to=toolPictureName)
    description = models.TextField(max_length=500)
    status = models.CharField(max_length=1, choices=app.constants.TOOL_STATUS)
    category = models.CharField(max_length=2, choices=app.constants.TOOL_CATEGORY)
    location = models.CharField(max_length=1, choices=app.constants.TOOL_LOCATION, blank=False, default='H')
    models.CharField()
    shed = models.ForeignKey(Shed, null=True, on_delete=models.SET_NULL)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    pickupArrangement = models.TextField(max_length=500)

    def __str__(self):
        return self.name

    def get_all_reservations(self):
        reservations = self.reservation_set.all()
        return reservations

    # returns a query of reservations on the tool based on the reservation_status arg (A, O, AC, R, C, etc.)
    def get_reservations(self, reservation_status):
        reservations = self.reservation_set.filter(status=reservation_status)
        return reservations

    # Checks if tool has unresolved future reservations that prevent it from moving
    # Returns true if no unresolved future reservations on it, false otherwise
    def is_ready_to_move(self):
        if self.location == "S":
            return False

        # Keeps a count of all reservations that might be interfering with moving a tool.
        blockingReservations = 0

        # Checks tool for any active reservations
        activeReservations = self.get_reservations('AC')
        blockingReservations = blockingReservations + len(activeReservations)

        # Checks tool for approved future reservations
        approvedReservations = self.get_reservations('A')
        blockingReservations = blockingReservations + len(approvedReservations)

        # Add additional reservations that might block tool from moving here
        user = self.owner
        ownReservations = app.models.Reservation.objects.filter(user = user)
        ownReservations = ownReservations.filter(status = "AC").filter(status ="A")
        blockingReservations = blockingReservations + len(ownReservations)

        # Check the sum of the lengths of the reservation lists described above.
        # If sum is zero (no blocking reservations), return ready_to_move = True. Else, return ready_to_move = False
        if blockingReservations == 0:
            return True
        else:
            return False

    def get_next_available_date(self):
        reservations = self.reservation_set.exclude(status='C').exclude(status='CL').exclude(status='O'). \
            exclude(status='P').exclude(status='R')
        blackoutdates = self.blackoutdate_set.all()
        availableDate = datetime.date.today()
        addOneDay = datetime.timedelta(days=1)
        setOfDates = set()

        for res in reservations:
            setOfDates = setOfDates.union(res.get_dates_covered())

        for bd in blackoutdates:
            setOfDates = setOfDates.union(bd.get_dates_covered())

        unavailableDates = sorted(setOfDates)

        for date in unavailableDates:
            while availableDate == date:
                availableDate = date + addOneDay

        return availableDate

    def get_days_until_available(self):
        today = datetime.date.today()
        delta = (self.get_next_available_date() - today).days
        return delta

    def get_status_label_owner(self):
        label = "Active"
        if self.status == "D":
            label = "Deactivated"
        else:
            reservations = self.get_all_reservations()
            for reservation in reservations:
                if reservation.status == "RI":
                    label = "Return Initiated"
                elif reservation.status == "O":
                    label = "Overdue"
                elif reservation.status == "AC":
                    label = "Lent Out"
        return label

    def get_label_type_owner(self):
        type = "label-success"
        if self.get_status_label_owner() == "Deactivated":
            type = "label-danger"
        if self.get_status_label_owner() == "Return Initiated":
            type = "label-warning"
        if self.get_status_label_owner() == "Overdue":
            type = "label-danger"
        if self.get_status_label_owner() == "Lent Out":
            type = "label-warning"
        return type

    def get_status_label_borrower(self):
        label = "Available"
        daysOnRes = self.get_days_until_available()
        if daysOnRes > 0:
            label = self.get_next_available_date()
        return label

    def get_label_type_borrower(self):
        type = "label-warning"
        if self.get_status_label_borrower() == "Available":
            type = "label-success"
        return type

    def get_init_return_reservation(self):
        reservations = self.get_reservations('RI')
        if len(reservations) > 0:
            return reservations[0]
        return reservations


    @property
    def address(self):
        if self.location == 'S':
            return self.shed.address
        return self.owner.address


class BlackoutDate(models.Model):
    class Meta:
        app_label = 'app'

    tool = models.ForeignKey(Tool)
    blackoutStart = models.DateField('From date')
    blackoutEnd = models.DateField('To date')

    def get_dates_covered(self):
        startDate = self.blackoutStart
        endDate = self.blackoutEnd
        addOneDay = datetime.timedelta(days=1)
        datesCovered = []
        while startDate <= endDate:
            datesCovered.append(startDate)
            startDate += addOneDay
        return datesCovered