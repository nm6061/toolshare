from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.views.generic import *
from django.shortcuts import render, render_to_response
from django.template.context import RequestContext
from django.http import HttpResponseRedirect
from app.forms.profile import UserProfileForm, UserProfileFormSet
from app import models
from collections import ChainMap
from app.views.edit import FormsetView
from app.forms.profile import ChangePasswordForm


class UserUpdateView(FormsetView):
    template_name = 'profile.html'
    model = models.User
    form_class = UserProfileForm
    formset_class = UserProfileFormSet
    permission_required = 'auth.change_user'
    headline = 'Change Profile'
    success_url = 'profile/'
    # success_message = 'Your profile settings has been saved'

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = form_class(instance=request.user)
        formset_class = self.get_formset_class()
        formset = formset_class(instance=request.user.address)
        return render(request, self.template_name, {'form': form, 'formset': formset})

    def form_valid(self, request, form, formset):
        # form_class = self.get_form_class()
        # form = self.get_form(form_class)
        # formset_class = self.get_formset_class()
        # formset = self.get_formset(formset_class)
        # if form.is_valid() and formset.is_valid():
        # self.object = form.save()
        #     form.instance = self.object
        form.save()
        # formset.instance = self.object
        formset.save()
        return HttpResponseRedirect('profile/')

        # return self.render_to_response(self.get_context_data(form=form))

    # def form_invalid(self, request, form, formset):
    #     return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(UserUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['userprofile_form'] = UserProfileFormSet(self.request.POST)
        else:
            context['userprofile_form'] = UserProfileFormSet()
        return context


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
    return render(request, 'password.html', {'form':form})