from django import forms
from django.forms import ModelForm
from app.models.shed import Shed
from app.models.account import Address
from django.core.exceptions import ObjectDoesNotExist

class shedForm(forms.ModelForm):

    class Meta:
        model = Shed
        fields = ['name']

        def clean_name(self):
            locname = self.cleaned_data['name']
            try:
                Shed.objects.get(name=locname)
            except ObjectDoesNotExist:
                return locname
            else:
                raise forms.ValidationError('Shed name is already taken')

        def save(self,commit=True):
            loc = super(shedForm, self).save(commit=False)
            if commit:
                loc.save()
                return loc


class shedAddress(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['street']

    def save(self, commit=True):
        add = super(shedAddress,self).save(commit=False)
        if commit:
            add.save()
            return add