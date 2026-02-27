from django import template
from badge.utils import get_owner_badge

register = template.Library()

@register.simple_tag
def owner_badge(owner):
    return get_owner_badge(owner)
