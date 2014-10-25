from django.conf.urls import patterns, url
from django.conf import settings
from django.conf.urls.static import static
# from django.contrib import admin
# admin.autodiscover()
from app.views.toolManagement import *

urlpatterns = patterns('',
    url(r'^registertool/$', 'app.views.registertool', name = 'registertool'),
    url(r'^tool/(?P<tool_id>\d+)/$', 'app.views.viewTool', name='viewTool'),
)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
