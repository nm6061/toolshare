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

@login_required(redirect_field_name='o')
def registertool(request):
    currentUser = request.user
    if request.method == 'POST':
        tool_form = AddToolForm(request.POST, request.FILES)

        if tool_form.is_valid():
            with transaction.atomic():
                new_tool = tool_form.save(commit=False)
                new_tool.owner = currentUser
                new_tool.status = 'A'
                new_tool.save()
                tool_form.save_m2m()

            tool_form = AddToolForm()
            return render(request, 'registertool.html',
                          RequestContext(request, {'form': tool_form, 'tool_added': True}))
        else:
            return render(request, 'registertool.html', RequestContext(request, {'form': tool_form}))
    else:
        tool_form = AddToolForm(initial = {'pickupArrangement': currentUser.pickup_arrangements})
        return render(request, 'registertool.html', RequestContext(request, {'form': tool_form}))


def viewTool(request, tool_id):
    currentUser = request.user
    tooldata = Tool.objects.get(id=tool_id)
    isToolOwner = tooldata.owner == currentUser
    context = {'tooldata': tooldata, 'isToolOwner':isToolOwner}
    return render(request, 'tool.html', context)