from django.db import models


class BlackoutDate(models.Model):
    blackoutStart = models.DateField()
    blackoutEnd = models.DateField()


class Tool(models.Model):
    name = models.CharField(max_length=20)
    pictureURL = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    # location = Address()
    status = models.CharField(max_length = 10)
    blackoutDates = models.ForeignKey(BlackoutDate)


