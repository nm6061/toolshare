from django.conf import settings
from django.db import models
from app.models import Tool


class Reservation(models.Model):
    from_date = models.DateField()
    to_date = models.DateField()
    status = models.CharField(max_length=15)

    tool = models.ForeignKey(Tool)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    def approve_reservation(self):
        return self.user.username

    def reject_reservation(self):
        return self.user.username