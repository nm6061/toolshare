from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from app.forms.shed import shedForm,shedAddress
from django.shortcuts import redirect
from django.template import RequestContext, loader
from django.views.generic import TemplateView
from app.models.shed import Membership


class MyShedsView(TemplateView):
    template_name = 'shedlist.html'
    def get(self, request):
        membership = Membership.objects.filter(user=request.user)
        template = loader.get_template('shedlist.html')
        context = RequestContext(request, {'membership': membership})
        return HttpResponse(template.render(context))


def shed_create_view(request):
    if request.method=='POST':
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
            messages.add_message(request, messages.WARNING, 'Shed creation error')
            return redirect('makeShed')
            context = RequestContext(request, {'shed_form': shedForm(), 'address_form': shedAddress()})
            template = loader.get_template('shedregister.html')
            return HttpResponse(template.render(context))