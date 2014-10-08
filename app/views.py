from django.shortcuts import render, render_to_response, redirect
from django.template.context import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from app import forms


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

            # TODO : REVIEW AND REWORK
            return render(request, 'dashboard.html', RequestContext(request, {}))
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


def Borrow(request):
    return render_to_response('Borrow.html')

def registertool(request):
    return render_to_response('registerTool.html')
    # TODO : Add register functionality