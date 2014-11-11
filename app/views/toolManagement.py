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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


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

            register_url = reverse_lazy("toolManagement:registerTool")

            #NOTE: the 'safe' extra_tag allows the string to be autoescaped so that links can be processed by the template.
            #It SHOULD NOT be used unless you need to add a hyperlink to your message!
            messages.success(request,'You have successfully registered a new tool! <br> <br> '
                                     '<a href="/tool/register_tool">Click here register another tool</a><br> OR <br> '
                                     '<a href=".">click here to return to your toolbox.</a>', extra_tags='safe')

            success_url = reverse_lazy("toolManagement:toolbox")
            return redirect(success_url)
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
        error_url = reverse_lazy("toolManagement:toolbox")
        messages.error(request,'Error! You do not have permission to edit this tool.<br> <br> <a href=".">Click here to return to the toolbox.</a>', extra_tags='safe')
        return redirect(error_url)
    if request.method == 'POST':
        tool_form = AddToolForm(request.POST or None, request.FILES or None, instance=tooldata)
        if tool_form.is_valid():
            tool_form.save()

            #NOTE: the 'safe' extra_tag allows the string to be autoescaped so that links can be processed by the template.
            #It SHOULD NOT be used unless you need to add a hyperlink to your message!
            messages.success(request,'Your tool has been successfully updated! <br> <br> <a href=".">Click here to go back to your tool.</a>', extra_tags='safe')

            success_url = reverse_lazy("toolManagement:viewTool", kwargs={'tool_id':tool_id})
            return redirect(success_url)
        else:
            return render(request, 'updatetool.html', RequestContext(request, {'form': tool_form}))
    else:
        tool_form = AddToolForm(instance=tooldata)
        return render(request, 'updatetool.html', RequestContext(request, {'form': tool_form}))


@login_required(redirect_field_name='o')
def toolbox(request):
    user = request.user
    toolList = Tool.objects.filter(owner_id=user)
    maxToolsPerPage = 12
    minToolsPerPage = 1
    paginator = Paginator(toolList, maxToolsPerPage, minToolsPerPage)
    page = request.GET.get('page')

    try:
        myTools = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        myTools = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        myTools = paginator.page(paginator.num_pages)

    context = {'myTools': myTools}
    return render(request, 'toolbox.html', context)