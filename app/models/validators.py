import re

from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator
from django.utils.encoding import force_text


class AlphabetOnlyValidator(BaseValidator):
    message = 'can contain only alphabets'
    code = 'alphabets_only'
    regex = re.compile('^[a-zA-Z ]+$')

    def __init__(self, message=None, code=None):
        if message:
            self.message = message
        if code:
            self.code = code

    def __call__(self, value):
        if not self.regex.search(force_text(value)):
            raise ValidationError(self.message, self.code, params={'value': value})


class AlphaNumericOnlyValidator(BaseValidator):
    message = 'cannot contain special characters'
    code = 'alphanumeric_only'
    regex = re.compile('^[a-zA-Z0-9]+$')

    def __init__(self, message=None, code=None):
        if message:
            self.message = message
        if code:
            self.code = code

    def __call__(self, value):
        if not self.regex.search(force_text(value)):
            raise ValidationError(self.message, self.code, params={'value': value})