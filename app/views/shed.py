from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import redirect
from django.template import loader
from django.template.context import RequestContext
from django.views.generic import TemplateView
from app.models.shed import Membership
from django.shortcuts import render
from app.forms.shed import shedAddress, shedForm


class MyShedsView(TemplateView):
    template_name = 'shedlist.html'
    def get(self, request):
        membership = Membership.objects.filter(user=request.user)
        template = loader.get_template('shedlist.html')
        context = RequestContext(request, {'membership': membership})
        return HttpResponse(template.render(context))


def shed_create_view(request):
    if request.method == 'POST':
        print('test')
        add_form = shedAddress(request.POST)
        sform = shedForm(request.POST)
        if add_form.is_valid() and sform.is_valid():
            address = add_form.save()
            shed = sform.save(commit=False)
            shed.address=address
            shed.owner=request.user
            shed.save()
            messages.add_message(request, messages.SUCCESS, 'Shed created successfuly')
            return redirect('mySheds')
        else:
            return render(request, 'shedregister.html', RequestContext(request, {'shed_form': shedForm, 'address_form': shedAddress}))
    else:
        template = loader.get_template('shedregister.html')
        return render(request, 'shedregister.html', RequestContext(request, {'shed_form': shedForm, 'address_form': shedAddress}))



            # messages.add_message(request, messages.WARNING, 'Shed creation error')
            # return redirect('makeShed')
            # context = RequestContext(request, {'shed_form': shedForm, 'address_form': shedAddress})
            # template = loader.get_template('shedregister.html')
            # return HttpResponse(template.render(context))
    # else:
    #     template = loader.get_template('shedregister.html')
    #     return render(
    #         request,
    #         template,
    #         context_instance= RequestContext(request,
    #             {'form':shedForm,
    #              'form':shedAddress,
    #             }))