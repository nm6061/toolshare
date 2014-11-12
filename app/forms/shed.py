from django import forms
from django.forms import ModelForm
from app.models.shed import Shed

class shedForm(ModelForm):
    name = forms.CharField(max_length=100)
    address = forms.CharField(max_length=100)

    class Meta:
        model = Shed
        fields = ['name', 'address']