from django.shortcuts import render, render_to_response, redirect
from django.template.context import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from app import forms
from app import models
from django.http import HttpResponse
from app.models import UserProfile, Reservation
from app.forms import UserUpdateForm
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.views.generic.edit import *


def home(request):
    return render_to_response('home.html')


def signout(request):
    logout(request)
    return render(request, 'home.html')


def signup(request):
    if request.method == 'POST':
        signup_form = forms.SignUpForm(request.POST)

        if signup_form.is_valid():
            with transaction.atomic():
                signup_form.save()

            signup_form = forms.SignUpForm()
            return render(request, 'signup.html',
                          RequestContext(request, {'form': signup_form, 'signup_successful': True}))
        else:
            return render(request, 'signup.html',
                          RequestContext(request, {'form': signup_form}))
    else:
        signup_form = forms.SignUpForm()
        return render(request, 'signup.html',
                      RequestContext(request, {'form': signup_form}))


def signin(request):
    if request.method == 'POST':
        signin_form = forms.SignInForm(request, request.POST)

        if signin_form.is_valid():
            user = authenticate(email=signin_form.cleaned_data['username'],
                                password=signin_form.cleaned_data['password'])
            login(request, user)

            if user == None:
                return render(request, 'signin.html',
                              RequestContext(request, {'form': signin_form, 'errors': 'Incorrect email or password'}))
            else:
                return render(request, 'dashboard.html')
        else:
            return render(request, 'signin.html', RequestContext(request, {'form': signin_form}))
    else:
        signin_form = forms.SignInForm()
    return render(request, 'signin.html', RequestContext(request, {'form': signin_form}))


@login_required(redirect_field_name='o')
def dashboard(request):
    return render_to_response('dashboard.html')


def browsetool(request):
    return render_to_response('browsetool.html')


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


def registertool(request):
    if request.method == 'POST':
        tool_form = forms.addToolForm(request.POST)

        if tool_form.is_valid():
            with transaction.atomic():
                new_tool = tool_form.save(commit=False)
                new_tool.owner = request.user
                new_tool.status = 'A'
                new_tool.save()
                tool_form.save_m2m()

            tool_form = forms.addToolForm()
            return render(request, 'registertool.html',
                          RequestContext(request, {'form': tool_form, 'tool_added': True}))
        else:
            return render(request, 'registertool.html', RequestContext(request, {'form': tool_form}))
    else:
        tool_form = forms.addToolForm()
        return render(request, 'registertool.html', RequestContext(request, {'form': tool_form}))


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


# def profile(request):
# return render_to_response('profile.html')
# @login_required(redirect_field_name='o')
class UserUpdateView(UpdateView):
    form_class = UserUpdateForm
    model = UserProfile
    # fields = ['first_name', 'last_name', 'apt_num', 'street', 'county', 'city', 'zip', 'phone_num', 'email',
    # 'pickup_arrangements']
    template_name = 'profile.html'
    permission_required = 'auth.change_user'
    headline = 'Change Profile'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        messages.success(self.request, 'Your profile settings has been saved')
        return reverse_lazy('profile')
