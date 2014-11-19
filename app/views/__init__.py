from django.http import HttpResponse
from django.shortcuts import render, render_to_response, redirect
from django.template.context import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.messages import views
from django.views.generic import edit
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from app import forms
from app import models
from app.forms.toolRegistration import AddToolForm
from app.models.reservation import Reservation
from app.models.tool import Tool
from django.db.models import Count
from app.models import User
from app.models import Shed
import datetime
from django.utils.timezone import utc
from django.http import HttpResponse

def home(request):
    if not request.user.is_authenticated():
        #temp_list = Tool.objects.values('tool')
        #new_list = list()
        #for iter_tool in temp_list:
         #   new_list.append(Tool.objects.filter(id=iter_tool['tool']).get())
        #temp_list = Tool.objects.values('tool')
        #new_tool_list = list()
        #for iter_tool in temp_list:
         #   new_tool_list.append(Tool.objects.filter(id=iter_tool['tool']).get())

        #temp2_list = Shed.objects.values('shed')
        #new_tool_list = list()
        #for iter_tool in temp_list:
         #   new_tool_list.append(Shed.objects.filter(id=iter_tool['shed']).get())

        return render_to_response('home.html')
    return render(request, 'auth_home.html')
    #return render(request, 'auth_home.html', RequestContext(request, {'new_tool': new_tool_list,
    #                                                                 'new_shed': new_shed_list}))




@login_required(redirect_field_name='o')
def browsetool(request):
    """
       browsetool() is responsible for rendering a web page displaying tools available
       for borrow.
       It currently filters tools by:
            -excluding tools belonging to the logged in user
            -excluding tools that have a 'deactivated' status
    """
    user = request.user
    tools = Tool.objects.exclude(owner_id=user).exclude(status='D')
    maxToolsPerPage = 12
    minToolsPerPage = 1
    paginator = Paginator(tools, maxToolsPerPage, minToolsPerPage)
    page = request.GET.get('page')
    try:
        toolsList = paginator.page(page)
    except PageNotAnInteger:
        toolsList = paginator.page(1)
    except EmptyPage:
        toolsList = paginator.page(paginator.num_pages)

    context = {'toolsList': toolsList}
    return render(request, 'browsetool.html', context)


def about(request):
    return render(request, 'about.html')

@login_required(redirect_field_name='o')
def presentstatistics(request):
    # presentstatistics= Reservation.objects.order_by('tool')
    temp_list = Reservation.objects.values('tool').distinct().annotate(total=Count('tool')).order_by('-total')
    popular_tool_list = list()
    for iter_tool in temp_list:
        popular_tool_list.append(Tool.objects.filter(id=iter_tool['tool']).get())

    temp2_list = Reservation.objects.values('user').distinct().annotate(total=Count('user')).order_by('-total')
    popular_borrower_list = list()
    for iter_tool in temp2_list:
        popular_borrower_list.append(User.objects.filter(id=iter_tool['user']).get())

    temp3_list = Tool.objects.values('owner').distinct().annotate(total=Count('owner')).order_by('-total')
    popular_lender_list = list()
    for iter_tool in temp3_list:
        popular_lender_list.append(User.objects.filter(id=iter_tool['owner']).get())

    #temp3_list = Reservation.objects.values('tool').distinct().annotate(total=Count('tool')).order_by('-total')
    #popular_lender_list = list()
    #for iter_tool in temp3_list:
      #  popular_lender_list.append(User.objects.filter(id=iter_tool['owner']).get())


    return render(request, 'presentstatistics.html', RequestContext(request, {'reservations': popular_tool_list,
                                                                              'borrower_list': popular_borrower_list,
                                                                                'lender_list': popular_lender_list}))


@login_required(redirect_field_name='o')
def reservation(request):
    reservations = Reservation.objects.filter(tool__owner=request.user, status='Pending')

    paginator = Paginator(reservations, 1) # Show 25 reservations per page

    page = request.GET.get('page')
    try:
        reservations = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        reservations = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        reservations = paginator.page(paginator.num_pages)

    return render(request, 'reservation.html', RequestContext(request, {'reservations': reservations}))


@login_required(redirect_field_name='o')
def ReservationHistory(request):
    reservations = Reservation.objects.filter(Q(status = "Reject") | Q(status = "Approved") |Q(status = "Cancel"), tool__owner=request.user)
    return render(request, 'ReservationHistory.html', RequestContext(request, {'reservations': reservations}))




@login_required(redirect_field_name='o')
@require_POST
def approve(request, reservation_id):
    reservation = Reservation.objects.get(pk=reservation_id)
    reservation.status = 'Approved'
    reservation.save()

    return render(request, 'approve_reservation.html', RequestContext(request, {'reservation': reservation}))


@login_required(redirect_field_name='o')
@require_POST
def reject(request, reservation_id):
    reservation = Reservation.objects.get(pk=reservation_id)
    return render(request, 'reject_reservation.html', RequestContext(request, {'reservation': reservation}))


@login_required(redirect_field_name='o')
@require_POST
def rejectmessage(request, reservation_id):
    csrfContext = RequestContext(request)
    reservation = Reservation.objects.get(pk=reservation_id)
    reservation.status = 'Reject'
    reservation.save()
    reservation.message = request.POST['message']
    reservation.save()

    return render(request, 'reject_accept.html', RequestContext(request, {'reservation': reservation}))


@login_required(redirect_field_name='o')
def requestsend(request):
    reservation = Reservation.objects.filter(user=request.user, status='Pending')

    return render(request, 'Reservation_me.html', RequestContext(request, {'reservation': reservation}))


@login_required(redirect_field_name='o')
@require_POST
def cancel(request, reservation_id):
    reservation = models.Reservation.objects.get(pk=reservation_id)
    reservation.status = 'Cancel'
    reservation.save()
    return render(request, 'cancel_reservation.html', RequestContext(request, {'reservation': reservation}))


# @login_required(redirect_field_name='o')
# @require_POST
# def reject(request, reservation_id):
# pass


@login_required(redirect_field_name='o')
def Borrow(request, tool_id):
    tool = Tool.objects.get(pk=tool_id)

    if request.method == 'POST':
        form = forms.BorrowToolForm(tool, request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reservation created successfully.')
            return render(request, 'borrow.html', RequestContext(request, {'form': form}))
            return render(request, 'borrow.html', RequestContext(request, {'form': form}))
        else:
            return render(request, 'borrow.html', RequestContext(request, {'form': form}))
    else:
        form = forms.BorrowToolForm(tool, request.user)
        return render(request, 'borrow.html', RequestContext(request, {'form': form}))





