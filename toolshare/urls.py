from django.conf.urls import patterns, include, url
from app.views import UserUpdateView
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'app.views.home', name = 'home'),
    url(r'^account/', include('app.urls.account', namespace='account')),
    url(r'^tool/', include('app.urls.toolManagement', namespace='toolManagement')),
    url(r'^dashboard/$', 'app.views.dashboard', name = 'dashboard'),
    url(r'^browsetool/$', 'app.views.browsetool', name = 'browsetool'),
    url(r'^tool/(?P<tool_id>\d+)/Borrow/$', 'app.views.Borrow', name = 'Borrow'),
    # url(r'^profile/$', 'app.views.profile', name = 'profile'),
    url(r'^profile/$', UserUpdateView.as_view(), name='profile'),
    url(r'^reservation/$', 'app.views.reservation', name = 'reservation'),
    url(r'^reservation/(?P<reservation_id>\d+)/approve/$', 'app.views.approve', name = 'approve'),
    url(r'^reservation/(?P<reservation_id>\d+)/reject/$', 'app.views.reject', name = 'reject'),
    url(r'^reservation/(?P<reservation_id>\d+)/cancel/$', 'app.views.cancel', name = 'cancel'),
)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
