from django.shortcuts import render, render_to_response, redirect
from django.template.context import RequestContext


def home(request):
    return render_to_response('home.html')


def signin(request):
    if request.method == 'POST':
        return redirect('/dashboard')
    return render_to_response('signin.html')


def dashboard(request):
    return render_to_response('dashboard.html')