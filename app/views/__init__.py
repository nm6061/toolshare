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


def home(request):
    return render_to_response('home.html')


@login_required(redirect_field_name='o')
def dashboard(request):
    user = request.user
    homeTools = models.Tool.objects.filter(owner_id=user).filter(location='H')
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
    user = request.user
    toolsList = models.Tool.objects.exclude(owner_id=user).exclude(status='D')
    context = {'toolsList': toolsList}
    return render(request,'browsetool.html', context)


@login_required(redirect_field_name='o')
def reservation(request):
    reservations = models.Reservation.objects.filter(tool__owner=request.user, status='Pending')

    return render(request, 'reservation.html', RequestContext(request, {'reservations': reservations}))


@login_required(redirect_field_name='o')
@require_POST
def approve(request, reservation_id):
    reservation = models.Reservation.objects.get(pk=reservation_id)
    reservation.status = 'Approved'
    reservation.save()

    return render(request, 'approve_reservation.html', RequestContext(request, {'reservation': reservation}))

@login_required(redirect_field_name='o')
@require_POST
def reject(request, reservation_id):
    reservation = models.Reservation.objects.get(pk=reservation_id)
    reservation.status = 'Reject'
    reservation.save()

    return render(request, 'reject_reservation.html', RequestContext(request, {'reservation': reservation}))


#@login_required(redirect_field_name='o')
#@require_POST
#def reject(request, reservation_id):
#    pass


@login_required(redirect_field_name='o')
def Borrow(request, tool_id):
    if request.method == 'POST':
        reservation = models.Reservation()
        reservation.user = request.user
        reservation.tool = models.Tool.objects.get(pk=tool_id)
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
def registertool(request):
    currentUser = request.user
    if request.method == 'POST':
        tool_form = forms.addToolForm(request.POST, request.FILES)

        if tool_form.is_valid():
            with transaction.atomic():
                new_tool = tool_form.save(commit=False)
                new_tool.owner = currentUser
                new_tool.status = 'A'
                new_tool.save()
                tool_form.save_m2m()

            tool_form = forms.addToolForm()
            return render(request, 'registertool.html',
                          RequestContext(request, {'form': tool_form, 'tool_added': True}))
        else:
            return render(request, 'registertool.html', RequestContext(request, {'form': tool_form}))
    else:
        tool_form = forms.addToolForm(initial = {'pickupArrangement': currentUser.pickup_arrangements})
        return render(request, 'registertool.html', RequestContext(request, {'form': tool_form}))


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

def viewTool(request, tool_id):
    currentUser = request.user
    tooldata = models.Tool.objects.get(id=tool_id)
    isToolOwner = tooldata.owner == currentUser
    context = {'tooldata': tooldata, 'isToolOwner':isToolOwner}
    return render(request, 'tool.html', context)
