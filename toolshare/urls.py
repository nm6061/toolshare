from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'app.views.home', name = 'home'),
    url(r'^signin/$', 'app.views.signin', name = 'signin'),
    url(r'^signup/$', 'app.views.signup', name = 'signup'),
    url(r'^signout/$', 'app.views.signout', name = 'signout'),
    url(r'^dashboard/$', 'app.views.dashboard', name = 'dashboard'),
    url(r'^browsetool/$', 'app.views.browsetool', name = 'browsetool'),
    url(r'^Borrow/$', 'app.views.Borrow', name = 'Borrow'),

    url(r'^registertool/$', 'app.views.registertool', name = 'registertool'),

    url(r'^approve_reservation/$', 'app.views.approve_reservation', name = 'approve_reservation'),
    url(r'^approve_success/$', 'app.views.approve_success', name = 'approve_success'),
)
