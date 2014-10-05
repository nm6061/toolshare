import ast
from django import template

register = template.Library()


@register.filter
def add_attrs(field, attrs):
    return field.as_widget(attrs=ast.literal_eval(attrs))