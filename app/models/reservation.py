from django.conf import settings
from django.db import models
from app.models import Tool
import app.constants
import datetime

class Reservation(models.Model):
    class Meta:
        app_label = 'app'

    from_date = models.DateField()
    to_date = models.DateField()
    status = models.CharField(max_length=2, choices=app.constants.RESERVATION_STATUSES)
    message = models.TextField(max_length = 200)
    tool = models.ForeignKey(Tool)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    def approve_reservation(self):
        return self.user.username

    def reject_reservation(self):
        return self.user.username

    def get_dates_covered(self):
        startDate = self.from_date
        endDate = self.to_date
        addOneDay = datetime.timedelta(days=1)
        datesCovered = []
        while startDate <= endDate:
            datesCovered.append(startDate)
            startDate += addOneDay
        return datesCovered