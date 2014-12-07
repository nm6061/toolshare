from django.shortcuts import render,  redirect
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from app.forms.toolRegistration import AddToolForm
from app.models.tool import Tool
from app.models.shed import Shed
from app.models import Reservation
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from app import forms
from django.db.models import Q
import datetime
import operator


@login_required()
def registerTool(request):
    currentUser = request.user
    sharezone = currentUser.share_zone[:5]
    sheds = Shed.objects.filter(address__zip__startswith = sharezone)
    invalidImage = False

    #check if uploaded file is an image or not
    for key,value in request.FILES.items():
        if not 'image' in value.content_type:
            invalidImage = True

    if request.method == 'POST':
        shedChoice = request.POST.get('shedChoice')

        if invalidImage:
            tool_form = AddToolForm(request.POST)

        else:
            tool_form = AddToolForm(request.POST, request.FILES)


        if tool_form.is_valid():
            with transaction.atomic():
                new_tool = tool_form.save(commit=False)
                new_tool.owner = currentUser
                new_tool.status = 'A'
                if new_tool.location == 'S':
                    new_tool.shed = Shed.objects.get(pk=shedChoice)
                new_tool.save()
                tool_form.save_m2m()

            #NOTE: the 'safe' extra_tag allows the string to be autoescaped so that links can be processed by the template.
            #It SHOULD NOT be used unless you need to add a hyperlink to your message!
            messages.success(request,'You have successfully added a new tool! <br> <br> '
                                     '<a href="/tool/register_tool">Click here if you wish to add another tool. </a>', extra_tags='safe')

            success_url = reverse_lazy("toolManagement:toolbox")
            return redirect(success_url)
        else:
            return render(request, 'registertool.html', RequestContext(request, {'form': tool_form, 'sheds':sheds, 'invalidImage':invalidImage}))
    else:
        tool_form = AddToolForm(initial = {'pickupArrangement': currentUser.pickup_arrangements})
        return render(request, 'registertool.html', RequestContext(request, {'form': tool_form, 'sheds':sheds}))


@login_required()
def viewTool(request, tool_id):
    tooldata = get_object_or_404(Tool, pk=tool_id)
    toolname = tooldata.name
    toolcategory = tooldata.category
    temp_list = Tool.objects.filter( Q( category = toolcategory) | Q( name__contains=toolname)).exclude(status='D')\
        .exclude(owner_id=request.user).exclude(pk = tool_id)
    similartools = temp_list.order_by('?')[:6]
    context = {'tooldata': tooldata, 'similartools':similartools}
    return render(request, 'tool.html', context)


@login_required()
def updateTool(request, tool_id):
    today = datetime.date.today()
    currentUser = request.user
    sharezone = currentUser.share_zone[:5]
    sheds = Shed.objects.filter(address__zip__startswith = sharezone)
    tooldata = get_object_or_404(Tool, pk=tool_id)
    denyAccess = True
    invalidImage = False

    #check if uploaded file is an image or not
    for key,value in request.FILES.items():
        if not 'image' in value.content_type:
            invalidImage = True

    if tooldata.owner == request.user:
        denyAccess = False

    if tooldata.location == 'S':
        if tooldata.shed.owner == request.user:
            denyAccess = False

    if denyAccess:
        error_url = reverse_lazy("toolManagement:toolbox")
        messages.error(request,'Error! You do not have permission to edit this tool.', extra_tags='safe')
        return redirect(error_url)

    # TODO : use tool is ready to move instead of futureres
    futureRes = tooldata.reservation_set.filter(Q( status='P') | Q( status='A'))
    unorderedDates = tooldata.blackoutdate_set.exclude(blackoutEnd__lt = today)
    blackoutdates = unorderedDates.order_by('blackoutStart')

    if request.method == 'POST':
        if 'updatetool' in request.POST:
            if invalidImage:
                updateform = AddToolForm(request.POST or None, instance=tooldata)
                messages.warning(request,'Tool picture was not updated because file was not an image.')
            else:
                updateform = AddToolForm(request.POST or None, request.FILES or None, instance=tooldata)

            blackoutform = forms.BlackoutDateForm(tooldata)
            shedChoice = request.POST.get('shedChoice')
            if updateform.is_valid():
                tool = updateform.save(commit=False)
                if tool.location == 'S':
                    tool.shed = Shed.objects.get(pk=shedChoice)
                tool.save()
                updateform.save_m2m()

                #NOTE: the 'safe' extra_tag allows the string to be autoescaped so that links can be processed by the template.
                #It SHOULD NOT be used unless you need to add a hyperlink to your message!
                messages.success(request,'Your tool was successfully updated! <br> <br> '
                                         '<a href="/tool/toolbox">Click here if you wish to return to your toolbox </a>', extra_tags='safe')
                return redirect('.')
            else:
                return render(request, 'updatetool.html', RequestContext(request, {'updateform': updateform,
                                'blackoutform': blackoutform, 'tool':tooldata, 'futureRes':futureRes, 'sheds':sheds, 'blackoutdates':blackoutdates}))
        elif 'addblackout' in request.POST:
            updateform = AddToolForm(instance=tooldata)
            blackoutform = forms.BlackoutDateForm(tooldata, request.POST)
            if blackoutform.is_valid():
                blackoutform.save()
                messages.success(request,'Blackout dates have been added to this tool. <br> <br> '
                                         '<a href="/tool/toolbox">Click here if you wish to return to your toolbox </a>', extra_tags='safe')
                return redirect('.')
            else:
                return render(request, 'updatetool.html', RequestContext(request, {'updateform': updateform,
                                'blackoutform': blackoutform, 'tool':tooldata, 'futureRes':futureRes, 'sheds':sheds, 'blackoutdates':blackoutdates}))
        elif 'deactivate' in request.POST:
            updateform = AddToolForm(request.POST or None, request.FILES or None, instance=tooldata)
            blackoutform = forms.BlackoutDateForm(tooldata)
            if updateform.is_valid():
                tool = updateform.save(commit=False)
                tool.status = 'D'
                tool.save()
                updateform.save_m2m()
                messages.success(request,'Your tool has been deactivated. <br> <br> '
                                         '<a href="/tool/toolbox">Click here if you wish to return to your toolbox </a>', extra_tags='safe')
                return redirect('.')
            else:
                updateform = AddToolForm(instance=tooldata)
                return render(request, 'updatetool.html', RequestContext(request, {'updateform': updateform,
                                'blackoutform': blackoutform, 'tool':tooldata, 'futureRes':futureRes, 'sheds':sheds, 'blackoutdates':blackoutdates}))
        elif 'activate' in request.POST:
            updateform = AddToolForm(request.POST or None, request.FILES or None, instance=tooldata)
            blackoutform = forms.BlackoutDateForm(tooldata)
            if updateform.is_valid():
                tool = updateform.save(commit=False)
                tool.status = 'A'
                tool.save()
                updateform.save_m2m()
                messages.success(request,'Your tool was successfully activated! <br> <br> '
                                         '<a href="/tool/toolbox">Click here if you wish to return to your toolbox </a>', extra_tags='safe')
                return redirect('.')
            else:
                return render(request, 'updatetool.html', RequestContext(request, {'updateform': updateform,
                                'blackoutform': blackoutform, 'tool':tooldata, 'futureRes':futureRes, 'sheds':sheds, 'blackoutdates':blackoutdates}))
        elif 'delete' in request.POST:
            dateID = request.POST['delete']
            dateToDelete = blackoutdates.get(pk=dateID)
            dateToDelete.delete()
            messages.success(request,'Blackout date was successfully deleted! <br> <br> '
                                         '<a href="/tool/toolbox">Click here if you wish to return to your toolbox </a>', extra_tags='safe')
            return redirect('.')
    else:
        updateform = AddToolForm(instance=tooldata)
        blackoutform = forms.BlackoutDateForm(tooldata)
        return render(request, 'updatetool.html', RequestContext(request, {'updateform': updateform,
                                'blackoutform': blackoutform, 'tool':tooldata, 'futureRes':futureRes, 'sheds':sheds, 'blackoutdates':blackoutdates}))


@login_required()
def toolbox(request, tool_filter):
    user = request.user
    dueDates = []
    if tool_filter == 'hometools':
        toolList = Tool.objects.filter(owner_id=user).filter(location='H')
    elif tool_filter == 'shedtools':
        toolList = Tool.objects.filter(owner_id=user).filter(location='S')
    else:
        toolList = Tool.objects.filter(owner_id=user)
    paginator = Paginator(toolList, 12, 1)
    page = request.GET.get('page')

    try:
        myTools = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        myTools = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        myTools = paginator.page(paginator.num_pages)

    context = {'myTools': myTools, 'filter': tool_filter, 'dueDates':dueDates}
    return render(request, 'toolbox.html', context)


@login_required()
def toolreturn(request):
    user = request.user
    today = datetime.date.today()
    approvedrequests = Reservation.objects.filter(user_id=user).filter(status="A")
    toolduedates = dict()

    for res in approvedrequests:
        if res.from_date <= today:
            daysleft = res.to_date - today
            tool = Tool.objects.get(pk = res.tool_id)
            toolduedates[tool] = daysleft.days

    sortedDates = sorted(toolduedates.items(), key=operator.itemgetter(1))

    paginator = Paginator(sortedDates, 12, 1)
    page = request.GET.get('page')

    try:
        toolreturns = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        toolreturns = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        toolreturns = paginator.page(paginator.num_pages)

    context = {'toolreturns': toolreturns, 'toolduedates':toolduedates,  'sortedDates':sortedDates}
    return render(request, 'toolreturn.html', context)