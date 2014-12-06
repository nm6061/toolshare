from collections import ChainMap
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, redirect, resolve_url
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import get_current_site
from django.views.generic import FormView, TemplateView
from django.contrib.auth import login, logout
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode, is_safe_url
from django.utils.encoding import force_bytes
from django.utils.decorators import method_decorator

from app.models.account import *
from app.forms.account import *
from app.views.edit import FormsetView


class SignUpView(FormsetView):
    template_name = 'account/signup.html'
    form_class = SignUpUserForm
    formset_class = SignUpAddressFormSet
    http_method_names = ['get', 'post']
    success_url = reverse_lazy('account:signin')
    success_message = 'We have sent you an activation email at <strong>%(email)s</strong>. Please follow the ' \
                      'instructions in the mail to <strong>activate</strong> your account.'

    def form_valid(self, request, form, formset):
        cleaned_data = dict()
        for k, v in ChainMap(formset.cleaned_data, form.cleaned_data).items():
            cleaned_data[k] = v
        self.sign_up(request, **cleaned_data)
        messages.success(request, self.success_message % {'email': cleaned_data['email']}, extra_tags='safe')
        return super(SignUpView, self).form_valid(request, form, formset)

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

    def get(self, request, *args, **kwargs):
        redirect_to = self.request.REQUEST.get(REDIRECT_FIELD_NAME, '')

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        kwargs = {'form': form, 'REDIRECT_FIELD_NAME': REDIRECT_FIELD_NAME, 'redirect_to': redirect_to}
        return self.render_to_response(self.get_context_data(**kwargs))


    def form_valid(self, form):
        redirect_to = self.request.REQUEST.get(REDIRECT_FIELD_NAME, '')

        # If redirection URL is un-safe redirect to default home
        if is_safe_url(url=redirect_to, host=self.request.get_host()):
            self.success_url = redirect_to

        login(self.request, form.get_user())
        return super(SignInView, self).form_valid(form)

    def form_invalid(self, form):
        return super(SignInView, self).form_invalid(form)


class SignOutView(FormView):
    http_method_names = ['post']
    success_url = reverse_lazy('account:signin')
    success_message = 'You have signed out of your ToolShare account.'

    def post(self, request):
        logout(request)
        messages.success(request, self.success_message)
        return redirect(self.success_url)


class ActivateAccountView(TemplateView):
    http_method_names = ['get']
    success_url = reverse_lazy('account:signin')
    success_message = 'Your ToolShare account is now ready to use. Please <strong>sign in</strong> to continue.'
    failure_url = reverse_lazy('account:signup')
    failure_message = 'It appears that the activation link is no longer valid. Please <strong>sign up</strong> for a ' \
                      'new account.'

    def get(self, request, activation_key):
        if RegistrationProfile.objects.activate_user(activation_key):
            messages.success(request, self.success_message, extra_tags='safe')
            return redirect(self.success_url)
        messages.error(request, self.failure_message, extra_tags='safe')
        return redirect(self.failure_url)


class RecoverAccountView(FormView):
    template_name = 'account/recover.html'
    success_url = reverse_lazy('account:signin')
    success_message = 'We have sent an email with instructions to <strong>reset</strong> the password on your ' \
                      'ToolShare account.'
    form_class = RecoverAccountForm
    http_method_names = ['get', 'post']

    def form_valid(self, form):
        user = User.objects.get(email=form.cleaned_data['email'])
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        form.save(get_current_site(self.request), user, uidb64, token)
        messages.success(self.request, self.success_message, extra_tags='safe')

        return super(RecoverAccountView, self).form_valid(form)


class ResetAccountView(FormView):
    template_name = 'account/reset.html'
    success_url = reverse_lazy('account:signin')
    success_message = 'The password on your ToolShare account was successfully reset. Please <strong>sign in' \
                      '</strong> with your new password.'
    failure_url = reverse_lazy('account:recover')
    failure_message = 'It appears that the URL you used to recover the account is no longer valid. Please try to ' \
                      'reset your password again.'
    form_class = ResetAccountForm
    http_method_names = ['get', 'post']

    def get(self, request, uidb64, token):
        uid = urlsafe_base64_decode(uidb64)
        user = User.objects.get(pk=uid)

        if not default_token_generator.check_token(user, token):
            messages.error(self.request, self.failure_message, extra_tags='safe')
            return redirect(self.failure_url)
        return super(ResetAccountView, self).get(request)

    def post(self, request, uidb64, token):
        uid = urlsafe_base64_decode(uidb64)
        user = User.objects.get(pk=uid)

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid():
            form.save(user)
            messages.success(self.request, self.success_message, extra_tags='safe')
            return super(ResetAccountView, self).form_valid(form)

        return super(ResetAccountView, self).form_invalid(form)


class UpdateAccountView(FormsetView):
    template_name = 'account/update.html'
    success_url = reverse_lazy('account:update')
    success_message = 'Your ToolShare account was successfully updated.'
    failure_message = \
        '''
        One or more reasons listed below is <strong>preventing</strong> the change from being saved:
        <ul>
            <li>You have <strong>borrowed tools</strong> in your possession that need to be returned.</li>
            <li>You have <strong>tools in the community shed</strong> that you need to collect.</li>
            <li>You have <strong>unresolved future reservations</strong>.</li>
        </ul>
        '''
    form_class = UpdateUserForm
    formset_class = UpdateAddressFormSet

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = form_class(instance=request.user)
        formset_class = self.get_formset_class()
        formset = formset_class(instance=request.user.address)
        return render(request, self.template_name, {'form': form, 'formset': formset})

    def post(self, request, *args, **kwargs):
        prev_sz = request.user.share_zone

        form_class = self.get_form_class()
        form = form_class(request.POST, instance=request.user)
        formset_class = self.get_formset_class()
        formset = formset_class(request.POST, instance=request.user.address)

        if form.is_valid() and formset.is_valid():
            if self.is_relocation_allowed(prev_sz, formset.instance.share_zone, request.user):
                return self.form_valid(request, form, formset)
            else:
                messages.error(request, self.failure_message % {'r': reverse_lazy('reservation')}, extra_tags='safe')
                return self.form_invalid(request, form, formset)
        else:
            return self.form_invalid(request, form, formset)

    def form_valid(self, request, form, formset):
        form.save()
        formset.save()
        messages.success(request, self.success_message)
        return super(UpdateAccountView, self).form_valid(request, form, formset)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UpdateAccountView, self).dispatch(request, *args, **kwargs)

    def is_relocation_allowed(self, prev_sz, curr_sz, user):
        if prev_sz != curr_sz and not user.is_ready_to_move():
            return False
        return True


class ChangePasswordView(FormView):
    template_name = 'account/change_password.html'
    success_url = reverse_lazy('account:update')
    success_message = 'Password updated successfully.'
    form_class = ChangePasswordForm

    def get_form(self, form_class):
        return form_class(user=self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        form.save()
        messages.success(self.request, self.success_message)
        return super(ChangePasswordView, self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ChangePasswordView, self).dispatch(request, *args, **kwargs)