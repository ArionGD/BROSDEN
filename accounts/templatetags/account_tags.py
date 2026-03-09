from django import template
from accounts.badge_utils import get_owner_badge

register = template.Library()

@register.simple_tag
def owner_badge(owner):
    return get_owner_badge(owner)
