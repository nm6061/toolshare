from django import forms
from django.forms import ModelForm
from app.models.shed import Shed
from app.models.account import Address
from django.forms.models import formset_factory

class shedForm(ModelForm):
    name = forms.CharField(max_length=100)
    address = forms.CharField(max_length=100)

    class Meta:
        model = Shed
        fields = ['name', 'address']


class shedAddress(ModelForm):
    class Meta:
        model = Address
        exclude = ['country']