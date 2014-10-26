from collections import ChainMap
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.sites.models import get_current_site
from django.views.generic import FormView, TemplateView
from django.contrib.auth import login, logout

from app.models.account import *
from app.forms.account import *
from app.views.edit import FormsetView


class SignUpView(FormsetView):
    template_name = 'account/signup.html'
    success_template_name = 'account/signup_success.html'
    form_class = SignUpUserForm
    formset_class = SignUpAddressFormSet
    http_method_names = ['get', 'post']
    success_url = reverse_lazy('account:signup_success')

    def form_valid(self, request, form, formset):
        cleaned_data = dict()
        for k, v in ChainMap(formset.cleaned_data, form.cleaned_data).items():
            cleaned_data[k] = v
        self.sign_up(request, **cleaned_data)
        return render(request, self.success_template_name)

    def sign_up(self, request, **cleaned_data):
        cd = cleaned_data

        # Attibutes of the User
        email, password, first_name, last_name, phone_num, pickup_arrangements = cd['email'], cd[
            'password1'], cd['first_name'], cd['last_name'], cd['phone_num'], cd['pickup_arrangements']

        # Attributes of user's Address
        apt_num, street, city, county, state, zip = cd['apt_num'], cd['street'], cd['city'], cd['county'], \
                                                    cd['state'], cd['zip']

        user = RegistrationProfile.objects.create_inactive_user(get_current_site(request), **cleaned_data)


class SignInView(FormView):
    template_name = 'account/signin.html'
    form_class = SignInForm
    http_method_names = ['get', 'post']
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super(SignInView, self).form_valid(form)

    def form_invalid(self, form):
        return super(SignInView, self).form_invalid(form)


class SignOutView(FormView):
    http_method_names = ['post']
    success_url = reverse_lazy('account:signout_success')

    def post(self, request):
        logout(request)
        return redirect(self.get_success_url())


class SignOutSuccessView(TemplateView):
    http_method_names = ['get']
    template_name = 'account/signout_success.html'


class ActivateAccountView(TemplateView):
    http_method_names = ['get']
    success_template_name = 'account/activation_success.html'

    def get(self, request, activation_key):
        # TODO : Determine what happens if activation fails.
        if RegistrationProfile.objects.activate_user(activation_key):
            return render(request, self.success_template_name)