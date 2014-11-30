from django import forms
from django.forms.models import save_instance
from django.forms.models import formset_factory

from app.models.shed import *
from app.models.account import Address


class RegisterShedForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(RegisterShedForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.error_messages = {'required': 'is required', 'invalid': 'is invalid'}

    def save(self, owner, address, commit=True):
        shed = Shed.objects.create(owner=owner, address=address, **self.cleaned_data)
        self.instance = shed
        fail_message = 'created'
        return save_instance(self, self.instance, self._meta.fields,
                             fail_message, commit, self._meta.exclude,
                             construct=False)


    class Meta:
        model = Shed
        fields = ['name']


class RegisterShedAddressForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(RegisterShedAddressForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.error_messages = {'required': 'is required', 'invalid': 'is invalid'}

    class Meta:
        model = Address
        exclude = ['country']


RegisterShedAddressFormSet = formset_factory(RegisterShedForm, RegisterShedAddressForm)


class UpdateShedForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UpdateShedForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.error_messages = {'required': 'is required', 'invalid': 'is invalid'}

    class Meta:
        model = Shed
        fields = ['name']


class UpdateShedAddressForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UpdateShedAddressForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.error_messages = {'required': 'is required', 'invalid': 'is invalid'}

    class Meta:
        model = Address
        exclude = ['country']


UpdateShedAddressFormSet = formset_factory(UpdateShedForm, UpdateShedAddressForm)