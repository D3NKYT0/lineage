from django import template
from django.template.loader import get_template, TemplateDoesNotExist

register = template.Library()

@register.simple_tag
def include_if_exists(template_name):
    try:
        get_template(template_name)
        return template_name
    except TemplateDoesNotExist:
        return ''
