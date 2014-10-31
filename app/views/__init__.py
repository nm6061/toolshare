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

from app import forms
from app import models
from app.forms.toolRegistration import AddToolForm
from app.models.reservation import Reservation
from app.models.tool import Tool
from django.db.models import Count

def home(request):
    return render_to_response('home.html')


@login_required(redirect_field_name='o')
def dashboard(request):
    user = request.user
    homeTools = Tool.objects.filter(owner_id=user).filter(location='H')
    context = {'homeTools': homeTools}
    return render(request, 'dashboard.html', context)


@login_required(redirect_field_name='o')
def browsetool(request):
    """
       browsetool() is responsible for rendering a web page displaying tools available
       for borrow.
       It currently filters tools by:
            -excluding tools belonging to the logged in user
            -excluding tools that have a 'deactivated' status
    """
    #user = request.user
    #toolsList = Tool.objects.exclude(owner_id=user).exclude(status='D')
    #context = {'toolsList': toolsList}
    return render(request,'browsetool.html')

@login_required(redirect_field_name='o')
def presentstatistics(request):
    # presentstatistics= Reservation.objects.order_by('tool')
    temp_list =  Reservation.objects.values('tool').distinct().annotate(total = Count('tool')).order_by('-total')
    popular_tool_list = list()
    for iter_tool in temp_list:
        popular_tool_list.append(Tool.objects.filter(id = iter_tool['tool']).get())

    return render(request, 'presentstatistics.html', RequestContext(request, {'reservations': popular_tool_list}))


@login_required(redirect_field_name='o')
def reservation(request):
    reservations = Reservation.objects.filter(tool__owner=request.user, status='Pending')

    return render(request, 'reservation.html', RequestContext(request, {'reservations': reservations}))


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
    reservation.status = 'Reject'
    reservation.save()

    return render(request, 'reject_reservation.html', RequestContext(request, {'reservation': reservation}))

@login_required(redirect_field_name='o')
@require_POST
def cancel(request, reservation_id):
    reservation = models.Reservation.objects.get(pk=reservation_id)
    reservation.status = 'Cancel'
    reservation.save()
    return render(request, 'cancel_reservation.html', RequestContext(request, {'reservation': reservation}))


#@login_required(redirect_field_name='o')
#@require_POST
#def reject(request, reservation_id):
#    pass


@login_required(redirect_field_name='o')
def Borrow(request, tool_id):
    if request.method == 'POST':
        reservation = Reservation()
        reservation.user = request.user
        reservation.tool = Tool.objects.get(pk=tool_id)
        reservation.status = 'Pending'

        borrow_tool_form = forms.BorrowToolForm(request.POST, instance=reservation)

        if borrow_tool_form.is_valid():
            borrow_tool_form.save()

            borrow_tool_form = forms.BorrowToolForm()
            return render(request, 'Borrow.html', RequestContext(request, {'form': borrow_tool_form, 'success': True}))
        else:
            return render(request, 'Borrow.html', RequestContext(request, {'form': borrow_tool_form}))

    else:
        borrow_tool_form = forms.BorrowToolForm()
        return render(request, 'Borrow.html', RequestContext(request, {'form': borrow_tool_form}))



@login_required(redirect_field_name='o')
def approve_reservation(request):
    # TODO GET CONTEXT
    def get_context_data(self, **kwargs):
        context = super(app.views.approve_reservation, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

    # TODO CHANGE STATUS TO RESERVED ON ACCEPT REQUEST
    if request.method == 'POST':
        toolForm = forms.ApproveReservationForm(request.POST)

        if toolForm.is_valid():
            with transaction.atomic():
                toolForm.save()

            toolForm = forms.ApproveReservationForm()
            return render(request, 'approve_reservation.html',
                          RequestContext(request, {'form': toolForm, 'tool_added': True}))
        else:
            return render(request, 'approve_reservation.html', RequestContext(request, {'form': toolForm}))
    else:
        toolForm = forms.ApproveReservationForm()
        return render(request, 'approve_reservation.html', RequestContext(request, {'form': toolForm}))


class UserUpdateView(edit.UpdateView):
    form_class = forms.UserUpdateForm
    model = models.UserProfile
    template_name = 'profile.html'
    permission_required = 'auth.change_user'
    headline = 'Change Profile'
    # success_message = 'Your profile settings has been saved'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        messages.success(self.request, 'changes to your ToolShare account have been saved.')
        return reverse_lazy('profile')


