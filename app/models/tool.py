from django.conf import settings
from django.db import models
from imagekit.models import ProcessedImageField
from pilkit.processors import Resize
from app.models.shed import Shed
import app.constants

class Tool(models.Model):
    class Meta:
        app_label = 'app'

    def toolPictureName(instance, filename):
        ext = filename.split('.')[-1]
        return 'toolpics/{}.{}'.format(instance.name, ext)

    name = models.CharField(max_length=25)
    picture = ProcessedImageField(processors=[Resize(500, 500)], format='JPEG', upload_to=toolPictureName)
    description = models.TextField(max_length=500)
    status = models.CharField(max_length=1, choices=app.constants.TOOL_STATUS)
    category = models.CharField(max_length=2, choices=app.constants.TOOL_CATEGORY)
    location = models.CharField(max_length=1, choices=app.constants.TOOL_LOCATION, blank=False, default='H')
    models.CharField()
    shed = models.ForeignKey(Shed, null=True, on_delete=models.SET_NULL)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    pickupArrangement = models.TextField(max_length=500)

    def __str__(self):
        return self.name

    @property
    def address(self):
        if self.location == 'S':
            return self.shed.address
        return self.owner.address


class BlackoutDate(models.Model):
    class Meta:
        app_label = 'app'

    tool = models.ForeignKey(Tool)
    blackoutStart = models.DateField()
    blackoutEnd = models.DateField()