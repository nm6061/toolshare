from django.conf.urls import patterns, include, url

from app.views.account import *

# TODO : Remove
from app.views.profile import *

urlpatterns = \
    patterns('',
             url(r'^signin/$', SignInView.as_view(), name='signin'),
             url(r'^signup/$', SignUpView.as_view(), name='signup'),
             url(r'^signout/$', SignOutView.as_view(), name='signout'),
             url(r'^recover/$', RecoverAccountView.as_view(), name='recover'),
             url(r'^update/$', UpdateAccountView.as_view(), name='update'),
             url(r'^activate/(?P<activation_key>[a-f0-9]{40})/$', ActivateAccountView.as_view(), name='activate'),
             url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
                 ResetAccountView.as_view(), name='activate'),
    )