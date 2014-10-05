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
        signup_user_form = forms.SignUpUserForm(request.POST)
        signup_address_form = forms.SignUpAddressForm(request.POST)

        if signup_user_form.is_valid() and signup_address_form.is_valid():
            # TODO : REVIEW AND REWORK
            return render(request, 'signin.html', RequestContext(request,{}))
        else:
            return render(request, 'signup.html',
                          RequestContext(request, {'user_form': signup_user_form, 'address_form': signup_address_form}))
    else:
        signup_user_form = forms.SignUpUserForm()
        signup_address_form = forms.SignUpAddressForm()
        return render(request, 'signup.html',
                      RequestContext(request, {'user_form': signup_user_form, 'address_form': signup_address_form}))

def browsetool(request):
    return render_to_response('browsetool.html')

def Borrow(request):
    return render_to_response('Borrow.html')