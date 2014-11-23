from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from app.views.profile import UserUpdateView
from app.views.shed import MyShedsView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    #Home Page
    url(r'^$', 'app.views.home', name = 'home'),
    url(r'^account/', include('app.urls.account', namespace='account')),
    #Tools
    url(r'^tool/', include('app.urls.toolManagement', namespace='toolManagement')),
    url(r'^browsetool/$', 'app.views.browsetool', name = 'browsetool'),
    url(r'^presentstatistics/$', 'app.views.presentstatistics', name = 'presentstatistics'),
    url(r'^tool/(?P<tool_id>\d+)/borrow/$', 'app.views.borrow', name = 'borrow'),
    #Reservations
    url(r'^reservation/$', 'app.views.reservation', name = 'reservation'),
    url(r'^ReservationHistory/$', 'app.views.ReservationHistory', name = 'ReservationHistory'),
    url(r'^Reservation_me/$', 'app.views.requestsend', name = 'Reservation_me'),
    url(r'^reservation/(?P<reservation_id>\d+)/approve/$', 'app.views.approve', name = 'approve'),
    url(r'^reservation/(?P<reservation_id>\d+)/reject/$', 'app.views.reject', name = 'reject'),
    url(r'^reservation/(?P<reservation_id>\d+)/cancel/$', 'app.views.cancel', name = 'cancel'),
    url(r'^reservation/(?P<reservation_id>\d+)/cancel/message/$', 'app.views.rejectmessage', name = 'rejectmessage'),
    #shed
    url(r'^sheds/$', MyShedsView.as_view(), name='mySheds'),
    url(r'^sheds/create$', 'app.views.shed.shed_create_view', name='makeShed')
)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
