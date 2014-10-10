from django.conf.urls import patterns, include, url
from app.views import UserUpdateView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'app.views.home', name = 'home'),
    url(r'^account/signin/$', 'app.views.signin', name = 'signin'),
    url(r'^account/signup/$', 'app.views.signup', name = 'signup'),
    url(r'^account/signout/$', 'app.views.signout', name = 'signout'),
    url(r'^dashboard/$', 'app.views.dashboard', name = 'dashboard'),
    url(r'^browsetool/$', 'app.views.browsetool', name = 'browsetool'),
    url(r'^Borrow/(?P<tool_id>\d+)/$', 'app.views.Borrow', name = 'Borrow'),
    # url(r'^profile/$', 'app.views.profile', name = 'profile'),
    url(r'^profile/$', UserUpdateView.as_view(), name='profile'),
    url(r'^registertool/$', 'app.views.registertool', name = 'registertool'),
    url(r'^approve_reservation/$', 'app.views.approve_reservation', name = 'approve_reservation'),
)
