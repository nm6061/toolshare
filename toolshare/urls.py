from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'app.views.index', name = 'index'),
    url(r'^signin/$', 'app.views.signin', name = 'signin')
)
