from django.db import models
from app.models.account import *

class Place(models.Model):
    name = models.CharField(max_length=100)
    sharezone = models.ForeignKey()
    owner = models.ForeignKey(User)
    address = models.CharField(max_length=100)

    def __str__(self):
        return self.name