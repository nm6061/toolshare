from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    middle_name = models.CharField(max_length=25)
    pickup_arrangements = models.CharField(max_length=100)
    phone_num = models.CharField(max_length=11)
    reputation = models.PositiveIntegerField(default=0)

    def UpdateUserInfo(self):
        pass

    def UpdatePreferences(self):
        pass

        # TODO : DEFINE METHOD AS SOON AS TOOL IS DEFINED
        # def Register(self, Tool):
        #    pass


class Address(models.Model):
    apartment_number = models.CharField(max_length=10)
    street = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    county = models.CharField(max_length=50)
    state = models.CharField(max_length=2)
    country = models.CharField(max_length=50)

    User = models.ForeignKey(User)