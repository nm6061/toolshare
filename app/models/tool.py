from django.conf import settings
from django.db import models
from imagekit.models import ProcessedImageField
from pilkit.processors import Resize



class Tool(models.Model):
    class Meta:
        app_label = 'app'

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
    picture = ProcessedImageField(processors=[Resize(500, 500)], format='JPEG', upload_to=toolPictureName)
    description = models.TextField(max_length=500)
    status = models.CharField(max_length=1, choices=STATUS)
    category = models.CharField(max_length=2, choices=CATEGORY)
    location = models.CharField(max_length=1, choices=LOCATION, blank=False, default=0)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    pickupArrangement = models.TextField(max_length=500)

    def __str__(self):
        return self.name


class BlackoutDate(models.Model):
    class Meta:
        app_label = 'app'

    tool = models.ForeignKey(Tool)
    blackoutStart = models.DateField()
    blackoutEnd = models.DateField()