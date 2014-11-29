from django.http import HttpResponse
from django.shortcuts import render, render_to_response, redirect
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
from django.conf import settings
from app import forms
from app import models
from app.models.reservation import Reservation
from app.models.tool import Tool
from django.db.models import Count
from app.models import User
from app.models import Shed
import datetime


import pdb



def home(request):
    # pdb.set_trace()
    if request.user.is_authenticated():
        toolsToShow = 6;
        shedsToShow = 3;
        temp_list = Tool.objects.all()
        temp_list = temp_list.order_by('pk')
        temp_list = temp_list.reverse()[:toolsToShow]

        temp2_list = Shed.objects.all()
        temp2_list = temp2_list.order_by('pk')
        temp2_list = temp2_list.reverse()[:shedsToShow]


        returned = Reservation.objects.filter(user=request.user, status='Approved')
        today1=datetime.date.today()
        final_list = list()

        for iter_reservation in returned:
            fromdate = iter_reservation.from_date
            todate = iter_reservation.to_date
            if fromdate >= today1:
                    delta=todate-today1
                    iter_reservation.diff = delta.days
                    final_list.append(iter_reservation)
                    print(str(iter_reservation.id)+"====>"+str(iter_reservation.diff))





        return render(request, 'auth_home.html', RequestContext(request, {'tools': temp_list, 'shed': temp2_list,  'returned': final_list,'now':datetime.date.today()}))
    return render(request, 'home.html')


@login_required(redirect_field_name='o')
def browsetool(request):
    """
       browsetool() is responsible for rendering a web page displaying tools available
       for borrow.
       It currently filters tools by:
            -excluding tools belonging to the logged in user
            -excluding tools that have a 'deactivated' status

    """
    # TODO : Add filter for share zone

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

        # temp3_list = Reservation.objects.values('tool').distinct().annotate(total=Count('tool')).order_by('-total')
        # popular_lender_list = list()
        # for iter_tool in temp3_list:
        # popular_lender_list.append(Tool.objects.filter(id=iter_tool['owner_id']).get())

    return render(request, 'presentstatistics.html', RequestContext(request, {'reservations': popular_tool_list,
                                                                              'borrower_list': popular_borrower_list,
                                                                              'lender_list': popular_lender_list}))


@login_required(redirect_field_name='o')
def reservation(request):
    reservations = Reservation.objects.filter(tool__owner=request.user, status='Pending')

    paginator = Paginator(reservations, 2)  # Show 25 reservations per page

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
    reservations1 = Reservation.objects.filter(Q(status="Reject"), tool__owner=request.user)
    reservations2 = Reservation.objects.filter(Q(status="Approved"), tool__owner=request.user)
    reservations3 = Reservation.objects.filter(Q(status="Cancel"))

    return render(request, 'ReservationHistory.html', RequestContext(request, {'reservations1': reservations1,
                                                                               'reservations2': reservations2,
                                                                               'reservations3': reservations3}))


@login_required(redirect_field_name='o')
@require_POST
def approve(request, reservation_id):
    reservation = Reservation.objects.get(pk=reservation_id)
    reservation.status = 'Approved'
    reservation.save()

    # Send the user who requested to borrow the tool an email
    subject = '[ToolShare] %(owner)s approved your request' % {'owner': reservation.tool.owner.get_short_name()}
    message = render_to_string('email/reservation_accepted.html', {'reservation': reservation})
    reservation.user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
    messages.success(request, '%(borrower)s\'s request to borrow %(tool)s was approved.' % {
        'borrower': reservation.user.get_short_name(), 'tool': reservation.tool.name})

    return redirect(reverse_lazy('reservation'))


@login_required(redirect_field_name='o')
@require_POST
def reject(request, reservation_id):
    reservation = Reservation.objects.get(pk=reservation_id)
    return render(request, 'reject_reservation.html', RequestContext(request, {'reservation': reservation}))


@login_required(redirect_field_name='o')
@require_POST
def rejectmessage(request, reservation_id):
    reservation = Reservation.objects.get(pk=reservation_id)
    reservation.status = 'Reject'
    reservation.message = request.POST['message']
    reservation.save()

    # Send the user who requested to borrow the tool an email
    subject = '[ToolShare] %(owner)s rejected your request' % {'owner': reservation.tool.owner.get_short_name()}
    message = render_to_string('email/reservation_rejected.html', {'reservation': reservation})
    reservation.user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
    messages.success(request, '%(borrower)s\'s request to borrow %(tool)s was rejected.' % {
        'borrower': reservation.user.get_short_name(), 'tool': reservation.tool.name})

    return redirect(reverse_lazy('reservation'))


@login_required(redirect_field_name='o')
def requestsend(request):
    reservation = Reservation.objects.filter(user=request.user, status='Pending')

    paginator = Paginator(reservation, 2)  # Show 25 reservations per page

    page = request.GET.get('page')
    try:
        reservation = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        reservation = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        reservation = paginator.page(paginator.num_pages)
    return render(request, 'Reservation_me.html', RequestContext(request, {'reservation': reservation}))


@login_required(redirect_field_name='o')
@require_POST
def cancel(request, reservation_id):
    reservation = models.Reservation.objects.get(pk=reservation_id)
    reservation.status = 'Cancel'
    reservation.save()
    return render(request, 'cancel_reservation.html', RequestContext(request, {'reservation': reservation}))


@login_required(redirect_field_name='o')
def borrow(request, tool_id):
    tool = Tool.objects.get(pk=tool_id)

    if request.method == 'POST':
        form = forms.BorrowToolForm(tool, request.user, request.POST)
        if form.is_valid():
            reservation = form.save()

            # Send the owner of the tool an email
            subject = '[ToolShare] %(borrower)s wants to borrow your tool' % {
                'borrower': reservation.user.get_short_name()}
            message = render_to_string('email/tool_reservation.html', {'reservation': reservation})
            tool.owner.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)

            messages.success(request, 'A request was successfully created. You will receive an email when the owner of '
                                      'the tool takes an action on your request.')
            return redirect(reverse_lazy('borrow', kwargs={'tool_id': tool_id}))
        else:
            return render(request, 'borrow.html', RequestContext(request, {'form': form}))
    else:
        form = forms.BorrowToolForm(tool, request.user)
        return render(request, 'borrow.html', RequestContext(request, {'form': form}))