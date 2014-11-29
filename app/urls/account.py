from django.conf.urls import patterns, include, url

from app.views.account import *

urlpatterns = \
    patterns('',
             url(r'^signin/$', SignInView.as_view(), name='signin'),
             url(r'^signup/$', SignUpView.as_view(), name='signup'),
             url(r'^signout/$', SignOutView.as_view(), name='signout'),
             url(r'^recover/$', RecoverAccountView.as_view(), name='recover'),
             url(r'^recover/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
                 ResetAccountView.as_view(), name='recovery_mailer'),
             url(r'^update/$', UpdateAccountView.as_view(), name='update'),
             url(r'^password/change/$', ChangePasswordView.as_view(), name='password_change'),
             url(r'^activate/(?P<activation_key>[a-f0-9]{40})/$', ActivateAccountView.as_view(),
                 name='activation_mailer')
    )