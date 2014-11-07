from collections import ChainMap
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.views.generic import FormView, TemplateView
from django.contrib.auth import login, logout
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes

from app.models.account import *
from app.forms.account import *
from app.views.edit import FormsetView


class SignUpView(FormsetView):
    template_name = 'account/signup.html'
    success_template_name = 'account/signup_success.html'
    form_class = SignUpUserForm
    formset_class = SignUpAddressFormSet
    http_method_names = ['get', 'post']

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
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super(SignInView, self).form_valid(form)

    def form_invalid(self, form):
        return super(SignInView, self).form_invalid(form)


class SignOutView(FormView):
    http_method_names = ['post']
    success_template_name = 'account/signout_success.html'

    def post(self, request):
        logout(request)
        return render(request, self.success_template_name)


class ActivateAccountView(TemplateView):
    http_method_names = ['get']
    success_template_name = 'account/activation_success.html'

    def get(self, request, activation_key):
        # TODO : Determine what happens if activation fails.
        if RegistrationProfile.objects.activate_user(activation_key):
            return render(request, self.success_template_name)


class RecoverAccountView(FormView):
    template_name = 'account/recover.html'
    success_template_name = 'account/recovery_success.html'
    form_class = RecoverAccountForm
    http_method_names = ['get', 'post']

    def form_valid(self, form):
        user = User.objects.get(email=form.cleaned_data['email'])
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        form.save(get_current_site(self.request), user, uidb64, token)

        return render(self.request, self.success_template_name)


class ResetAccountView(FormView):
    template_name = 'account/reset.html'
    success_template_name = 'account/reset_success.html'
    invalid_link_template_name = 'account/reset_invalid.html'
    form_class = ResetAccountForm
    http_method_names = ['get', 'post']

    def get(self, request, uidb64, token):
        uid = urlsafe_base64_decode(uidb64)
        user = User.objects.get(pk=uid)

        if not default_token_generator.check_token(user, token):
            return render(self.request, self.invalid_link_template_name)
        return super(ResetAccountView, self).get(request)

    def post(self, request, uidb64, token):
        uid = urlsafe_base64_decode(uidb64)
        user = User.objects.get(pk=uid)

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid():
            form.save(user)
            return render(self.request, self.success_template_name)

        return super(ResetAccountView, self).form_invalid(form)


class UpdateAccountView(FormsetView):
    template_name = 'account/update.html'
    form_class = UpdateUserForm
    formset_class = UpdateAddressFormSet
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
        messages.success(request, message='Changes to your account were saved successfully.')
        return redirect(self.success_url)