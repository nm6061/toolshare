from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, RequestContext, render
from app.models.account import *
from app.forms.shed import shedForm
from django.http import HttpResponseRedirect


# @login_required(redirect_field_name='o')
def listshed(request):
    user, sharezone = basic(request)
    # places = sharezone.place_set.all()
    # places = sharezone.place_set.all()

    # if 'place' in request.GET:
    #     if 'edit' in request.GET:
    #         return editShed(request)
    #
    #     p = User.share_zone.place_set.get(pk=request.GET['place'])
    #     user_from_sharezone=User.objects.get(place__id__exact=p.id)
    #     return render_to_response('sheddetail.html', locals(), context_instance=RequestContext(request))
    return render_to_response('shedlist.html', locals(), context_instance=RequestContext(request))

# @login_required(redirect_field_name='o')
def registershed(request):
    user = User.objects.get(pk=request.user.pk)
    sharezone = User.share_zone

    if request.method =='POST':
        f = shedForm(request.POST)
        if (f.is_valid()):
            new_place = f.save(commit=False)
            m = User.objects.get(username=request.user.username)
            new_place.owner = m
            new_place.sharezone= m.share_zone
            new_place.save()
            f.save()
            return HttpResponseRedirect('/shedlist/')
        else:
            f = shedForm()

            return render_to_response('shedregister.html', locals(), context_instance=RequestContext(request))

@login_required(redirect_field_name='o')
def editShed(request):
    user,sharezone=basic(request)
    if request.method == 'POST':
        p = User.share_zone.place_set.get(pk=request.GET['place'])
        tools = p.tool_set.all()

        f = shedForm(request.POST, instance=p)
        if f.is_valid():
            f.save()

        return HttpResponseRedirect()

    else:
        p = ShareZone.place_set.get(pk=request.GET['place'])
        tools = p.tool_set.all()

        if 'delete' in request.GET:
            for t in p.tool_set.all():
                for r in t.reservation_set.all():
                    r.delete()
                    t.delete()
                    p.delete()
                    request.GET=request.GET.copy()
                    del request.GET['edit']
                    del request.GET['delete']
                    return render(request, 'shedlist.html')

                f = shedForm (instance=p)
                return render_to_response('sheddetail.html', locals(), context_instance = RequestContext(request))

def basic(request):
    user = User.objects.get(pk=request.user.pk)
    sharezone = User.share_zone
    return user,sharezone