from django.conf.urls import patterns, include, url

from app.views.shed import *

urlpatterns = \
    patterns('',
             url(r'^register/$', RegisterShedView.as_view(), name='register'),
             url(r'^$', IndexShedView.as_view(), name='index'),
             url(r'^(?P<shed_id>\d+)/$', ShedDetailView.as_view(), name='detail'),
             url(r'^(?P<shed_id>\d+)/update/$', UpdateShedView.as_view(), name='update'),
    )