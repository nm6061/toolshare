from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    #Home Page
    url(r'^$', 'app.views.home', name = 'home'),
    url(r'^account/', include('app.urls.account', namespace='account')),
    url(r'^shed/', include('app.urls.shed', namespace='shed')),
    #Tools
    url(r'^tool/', include('app.urls.toolManagement', namespace='toolManagement')),
    url(r'^browsetool/$', 'app.views.browsetool', name = 'browsetool'),
    url(r'^presentstatistics/$', 'app.views.presentstatistics', name = 'presentstatistics'),
    url(r'^tool/(?P<tool_id>\d+)/borrow/$', 'app.views.borrow', name = 'borrow'),
    #Reservations
    url(r'^reservation/in/$', 'app.views.reservation', name = 'reservation'),
    url(r'^reservation/out/$', 'app.views.requestsend', name = 'Reservation_me'),
    url(r'^reservation/history/$', 'app.views.ReservationHistory', name = 'ReservationHistory'),
    url(r'^reservation/(?P<reservation_id>\d+)/initate_return/$', 'app.views.initiate_return', name = 'initiate_return'),
    url(r'^reservation/(?P<reservation_id>\d+)/approve/$', 'app.views.approve', name = 'approve'),
    url(r'^reservation/(?P<reservation_id>\d+)/reject/$', 'app.views.reject', name = 'reject'),
    url(r'^reservation/(?P<reservation_id>\d+)/cancel/$', 'app.views.cancel', name = 'cancel'),
    url(r'^reservation/(?P<reservation_id>\d+)/abc/$', 'app.views.abc', name = 'abc'),
)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'app.views.page_not_found'