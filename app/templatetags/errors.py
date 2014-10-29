import ast
from django import template

register = template.Library()


@register.inclusion_tag('errors.html')
def errors(*forms):
    field_errors = []
    form_errors = []

    for form in forms:
        if form.errors:
            field_errors = field_errors + [{'name': field.label, 'errors': [error for error in field.errors]} for field
                                           in form if field.errors]
        if form.non_field_errors():
            form_errors = form_errors + [{'errors': [error for error in form.non_field_errors()]}]

    return {'has_errors': len(form_errors) > 0 or len(field_errors) > 0, 'form_errors': form_errors,
            'field_errors': field_errors}