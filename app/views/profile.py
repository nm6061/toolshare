from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.views.generic import *
from django.shortcuts import render, render_to_response
from django.template.context import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from app.forms.profile import UserProfileForm, UserProfileFormSet
from app import models
from collections import ChainMap
from app.views.edit import FormsetView
from app.forms.profile import ChangePasswordForm


class UserUpdateView(FormsetView):
    template_name = 'profile.html'
    form_class = UserProfileForm
    formset_class = UserProfileFormSet
    success_url = reverse_lazy('account:update')

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = form_class(instance=request.user)
        formset_class = self.get_formset_class()
        formset = formset_class(instance=request.user.address)
        return render(request, self.template_name, {'form': form, 'formset': formset})

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = form_class(request.POST, instance=request.user)
        formset_class = self.get_formset_class()
        formset = formset_class(request.POST, instance=request.user.address)

        if form.is_valid() and formset.is_valid():
            return self.form_valid(request, form, formset)
        else:
            return self.form_invalid(request, form, formset)

    def form_valid(self, request, form, formset):
        form.save()
        formset.save()
        messages.success(request, message='Changes to your ToolShare account were saved successfully.')
        return redirect(self.success_url)


def password(request):
    user = request.user
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data.get('new_password')
            user.set_password(new_password)
            user.save()
            messages.add_message(request, messages.SUCCESS, 'Your password were successfully changed.')
    else:
        form = ChangePasswordForm(instance=user)
    return render(request, 'password.html', {'form': form})