from django import forms
from app import models
from app.models.tool import Tool



class AddToolForm(forms.ModelForm):
    class Meta:
        model = Tool
        fields = ['name', 'description', 'category', 'location', 'picture', 'pickupArrangement']
        widgets = {
            'location': forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        super(AddToolForm, self).__init__(*args, **kwargs)

        self.fields['name'].error_messages = {'required': 'Please enter a name for the tool.'}
        self.fields['description'].error_messages = {'required': 'Please provide a description of your tool.'}
        self.fields['category'].error_messages = {'required': 'Please choose which category your tool falls into.'}
        self.fields['location'].error_messages = {'required': 'Please choose where your tool will be shared from.'}
        self.fields['picture'].error_messages = {'required': 'Please upload a picture of the tool.'}
        self.fields['pickupArrangement'].error_messages = {'required': 'Please specify a pickup arrangement.'}

    def clean_name(self):
        return self.cleaned_data['name'].strip().capitalize()

    def clean_description(self):
        return self.cleaned_data['description'].strip().capitalize()

    def clean_pickupArrangement(self):
        return self.cleaned_data['pickupArrangement'].strip().capitalize()