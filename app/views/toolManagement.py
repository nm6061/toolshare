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
from django.shortcuts import get_object_or_404


@login_required(redirect_field_name='o')
def registerTool(request):
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

            tool_form = AddToolForm(initial = {'pickupArrangement': currentUser.pickup_arrangements})
            messages.success(request, 'yay new tool added!')
            return render(request, 'registertool.html', RequestContext(request, {'form': tool_form, 'tool_added': True, 'messages':messages}))
        else:
            return render(request, 'registertool.html', RequestContext(request, {'form': tool_form}))
    else:
        tool_form = AddToolForm(initial = {'pickupArrangement': currentUser.pickup_arrangements})
        return render(request, 'registertool.html', RequestContext(request, {'form': tool_form}))


@login_required(redirect_field_name='o')
def viewTool(request, tool_id):
    currentUser = request.user
    tooldata = get_object_or_404(Tool, pk=tool_id)
    isToolOwner = tooldata.owner == currentUser
    context = {'tooldata': tooldata, 'isToolOwner':isToolOwner}
    return render(request, 'tool.html', context)


@login_required(redirect_field_name='o')
def updateTool(request, tool_id):
    tooldata = get_object_or_404(Tool, pk=tool_id)
    if not tooldata.owner == request.user:
        return HttpResponse("You don't have permission to edit this tool!")
    if request.method == 'POST':
        tool_form = AddToolForm(request.POST or None, request.FILES or None, instance=tooldata)
        if tool_form.is_valid():
            tool_form.save()
            success_url = reverse_lazy("toolManagement:viewTool", kwargs={'tool_id':tool_id})

            #NOTE: the 'safe' extra_tag allows the string to be autoescaped so that links can be processed by the template.
            #It SHOULD NOT be used unless you need to add a hyperlink to your message!
            messages.success(request,'Your tool has been successfully updated! <br> <br> <a href=".">Click here to go back to your tool.</a>', extra_tags='safe')

            return redirect(success_url)
        else:
            return render(request, 'updatetool.html', RequestContext(request, {'form': tool_form}))
    else:
        tool_form = AddToolForm(instance=tooldata)
        return render(request, 'updatetool.html', RequestContext(request, {'form': tool_form}))


@login_required(redirect_field_name='o')
def toolbox(request):
    user = request.user
    homeTools = Tool.objects.filter(owner_id=user).filter(location='H')
    context = {'homeTools': homeTools}
    return render(request, 'toolbox.html', context)