from django.shortcuts import render
from django.template.context import RequestContext

def index(request):
    """Renders home page"""
    return render(
        request,
        'index.html',
        RequestContext(request, {
            'title' : 'Welcome to Tool Share',
            'message' : 'Watch this space for more...'
        })
    )
