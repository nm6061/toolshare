from django.shortcuts import render, render_to_response, redirect
from django.template.context import RequestContext
from app import forms


def home(request):
    return render_to_response('home.html')


def signin(request):
    if request.method == 'POST':
        return redirect('/dashboard')
    return render(request, 'signin.html', RequestContext(request))


def dashboard(request):
    return render_to_response('dashboard.html')


def signup(request):
    if request.method == 'POST':
        signup_form = forms.SignUpForm(request.POST)

        if signup_form.is_valid():
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

def browsetool(request):
    return render_to_response('browsetool.html')

def Borrow(request):
    return render_to_response('Borrow.html')