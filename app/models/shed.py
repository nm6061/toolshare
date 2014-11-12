from django.db import models
from app.models.account import *

class Shed(models.Model):
    class Meta:
        app_label = 'app'

    name = models.CharField(max_length=100)
    sharezone = models.ForeignKey(ShareZone)
    owner = models.ForeignKey(User)
    address = models.CharField(max_length=100)

    def __str__(self):
        return self.name