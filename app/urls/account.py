from django.conf.urls import patterns, include, url

from app.views.account import *

urlpatterns = \
    patterns('',
             url(r'^signin/$', SignInView.as_view(), name='signin'),
             url(r'^signup/$', SignUpView.as_view(), name='signup'),
             url(r'^signup/success/$', SignUpSuccessView.as_view(), name='signup_success'),
             url(r'^signout/$', SignOutView.as_view(), name='signout'),
             url(r'^signout/success/$', SignOutSuccessView.as_view(), name='signout_success')
    )