from django.db import models
from django.core.urlresolvers import reverse

from app.models.account import *
from app.models.tool import *
from app.models.reservation import *


class UserProfile(models.Model):
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=True)
    phone_num = models.CharField(max_length=11, default='', blank=True)
    email = models.EmailField(unique=True, blank=False)
    pickup_arrangements = models.TextField(max_length=100, default='', blank=True)
    apt_num = models.CharField(max_length=10, default='', blank=True)
    street = models.CharField(max_length=50, default='', blank=False)
    city = models.CharField(max_length=50, default='', blank=False)
    county = models.CharField(max_length=50, default='', blank=True)
    state = models.CharField(max_length=2, default='app.models.User.state', blank=False)
    country = models.CharField(max_length=50, default='USA', blank=False)
    zip = models.CharField(max_length=9, default='', blank=False)

    # def __iadd__(self, state):
    # state = app.models.User.state

    def __unicode__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('profile', kwargs={'username': self.user.username})


