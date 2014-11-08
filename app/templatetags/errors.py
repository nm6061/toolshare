import ast, json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.inclusion_tag('errors.html')
def errors(*forms):
    field_errors = []
    form_errors = []

    for form in forms:
        if form.errors:
            field_errors = field_errors + \
                           [{'id': field.auto_id, 'name': field.label, 'errors': [error for error in field.errors]}
                            for field in form if field.errors]

        if form.non_field_errors():
            form_errors = form_errors + [{'errors': [error for error in form.non_field_errors()]}]

    has_errors = len(form_errors) > 0 or len(field_errors) > 0
    error_field_ids = mark_safe(json.dumps([field['id'] for field in field_errors]))

    return {'has_errors': has_errors, 'error_field_ids': error_field_ids, 'form_errors': form_errors,
            'field_errors': field_errors}