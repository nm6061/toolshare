from django.shortcuts import render, render_to_response, redirect
from django.template.context import RequestContext
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from app import forms, models
from django.http import HttpResponse
from app.models import UserProfile, Reservation, Tool
from app.forms import UserUpdateForm, addReservationForm
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.views.generic.edit import *

# TODO : REMOVE
from django.contrib.auth.models import AnonymousUser


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


@login_required
def Borrow(request, tool_id):
    if request.method == 'POST':
        reservation = Reservation()

        return HttpResponse(isinstance(get_user_model(), ))
        reservation.tool = Tool.objects.get(pk=tool_id)
        reservation.user = get_user_model()


        reservation_form = addReservationForm(request.POST, instance=reservation)

        if reservation_form.is_valid():
            reservation_form.save()

            return HttpResponse('Saved...')
        else:
            return render(request, 'Borrow.html', RequestContext(request, {'form': reservation_form}))
    else:
        reservation_form = addReservationForm()
        return render(request, 'Borrow.html', RequestContext(request, {'form': reservation_form}))


def registertool(request):
    if request.method == 'POST':
        toolForm = forms.addToolForm(request.POST)

        if toolForm.is_valid():
            with transaction.atomic():
                toolForm.save()

            toolForm = forms.addToolForm()
            return render(request, 'registertool.html',
                          RequestContext(request, {'form': toolForm, 'tool_added': True}))
        else:
            return render(request, 'registertool.html', RequestContext(request, {'form': toolForm}))
    else:
        toolForm = forms.addToolForm()
        return render(request, 'registertool.html', RequestContext(request, {'form': toolForm}))


def approve_reservation(request):
    if request.method == 'GET':
        return render(request, 'approve_success.html',
                      RequestContext(request))


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
