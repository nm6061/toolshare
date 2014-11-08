from django import forms
from django.forms import ModelForm
from app.models.shed import Place

class placeForm(ModelForm):
    name = forms.CharField(max_length=100)
    address = forms.CharField(max_length=100)

    class Meta:
        model = Place
        fields = ['name', 'address']