from django.shortcuts import render,render_to_response
from django.template.context import RequestContext

def index(request):
    """Renders home page"""
    return render(
        request,
        'index.html',
        RequestContext(request, {
            'title': 'Welcome to Tool Share',
            'message': 'Watch this space for more...'
        })
    )

def signin(request):
    """Renders the user sign in page"""
    return render_to_response('signin.html')