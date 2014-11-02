import app.constants
from django.core.urlresolvers import reverse
from app.models.account import *
from django.db import models


class Address(models.Model):
    apt_num = models.CharField('apartment number', max_length=10, blank=True)
    street = models.CharField('street', max_length=50)
    city = models.CharField('city', max_length=50, validators=[AlphabetOnlyValidator()])
    county = models.CharField('county', max_length=50, default='', blank=True, validators=[AlphabetOnlyValidator()])
    state = models.CharField('state', max_length=2, choices=app.constants.US_STATES)
    country = models.CharField('country', max_length=50, default='USA')
    zip = models.CharField('zip code', max_length=9, validators=[
        RegexValidator(regex='^\d{5}(?:[-\s]\d{4})?$', message='should be 5 or 9 digits',
                       code='invalid_phone')])

    def __unicode__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('profile', kwargs={'username': self.user.username})

    class Meta:
        app_label = 'app'


class User(AbstractBaseUser):
    first_name = models.CharField('first name', max_length=30, validators=[AlphabetOnlyValidator()])
    last_name = models.CharField('last name', max_length=30, blank=True, validators=[AlphabetOnlyValidator()])
    phone_num = models.CharField('phone number', max_length=11, blank=True, validators=[
        RegexValidator(regex='^\d{9,10}$', message='should be 9 or 10 digits', code='invalid_phone')])
    email = models.EmailField('email address', unique=True, validators=[EmailValidator()])
    pickup_arrangements = models.TextField('pickup arrangements', max_length=100, blank=True)

    def __unicode__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('profile', kwargs={'username': self.user.username})

    # address = models.ForeignKey(Address, unique=True)

    class Meta:
        app_label = 'app'