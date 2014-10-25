from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, User
from django.core.urlresolvers import reverse
from django.conf import settings
import app.constants
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToCover
from app.models.account import User


class Tool(models.Model):
    STATUS = (
        ('A', 'Available'),
        ('D', 'Deactivated'),
        ('L', 'Lent out'),
    )

    LOCATION = (
        ('H', 'Home'),
        ('S', 'Shed')
    )

    CATEGORY = (
        ('BL', 'Blades'),
        ('BR', 'Braces'),
        ('BS', 'Brushes'),
        ('CA', 'Calipers'),
        ('CH', 'Chisel'),
        ('CL', 'Clamps'),
        ('CP', 'Clips'),
        ('CM', 'Compressors'),
        ('CU', 'Cutters'),
        ('DI', 'Dispenser'),
        ('DR', 'Drills'),
        ('GA', 'Gauges'),
        ('GR', 'Grinder'),
        ('HA', 'Hammer'),
        ('HX', 'Hand Axe'),
        ('HT', 'Hedge Trimmers'),
        ('LA', 'Ladders'),
        ('LM', 'Lawn Mowers'),
        ('MT', 'Measuring Tape/Ruler'),
        ('MI', 'Micrometer'),
        ('NG', 'Nail Gun'),
        ('PL', 'Pliers'),
        ('SA', 'Sanders'),
        ('SW', 'Saws'),
        ('SC', 'Scissors'),
        ('SD', 'Screwdrivers'),
        ('SH', 'Shovel'),
        ('TB', 'Toolbox'),
        ('TR', 'Trowel'),
        ('WE', 'Welding/ Soldering'),
        ('WR', 'Wrenches'),
        ('OT', 'Other'),
    )

    def toolPictureName(instance, filename):
        ext = filename.split('.')[-1]
        return 'toolpics/{}.{}'.format(instance.name, ext)

    name = models.CharField(max_length=25)
    picture = ProcessedImageField(processors=[ResizeToCover(200, 200)], format='JPEG', upload_to=toolPictureName)
    description = models.TextField(max_length=500)
    status = models.CharField(max_length=1, choices=STATUS)
    category = models.CharField(max_length=2, choices=CATEGORY)
    location = models.CharField(max_length=1, choices=LOCATION, blank=False, default=0)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    pickupArrangement = models.TextField(max_length=500)

    def __str__(self):
        return self.name


class BlackoutDate(models.Model):
    tool = models.ForeignKey(Tool)
    blackoutStart = models.DateField()
    blackoutEnd = models.DateField()


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