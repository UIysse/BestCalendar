from django import template
from django.forms.widgets import TextInput

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css):
    return field.as_widget(attrs={"class":css})