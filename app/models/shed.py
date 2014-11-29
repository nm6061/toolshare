from django.db import models

from app.models.account import *


class Shed(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=False)
    registered_on = models.DateTimeField(auto_now_add=True)

    # Foreign keys
    owner = models.ForeignKey(User)
    address = models.ForeignKey(Address)

    class Meta:
        app_label = 'app'

    def __str__(self):
        return self.name