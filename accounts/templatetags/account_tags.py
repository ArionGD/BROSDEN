from django import template
from accounts.badge_utils import get_owner_badge

register = template.Library()

@register.simple_tag
def owner_badge(owner):
    return get_owner_badge(owner)

@register.filter
def multiply(value, arg):
    """Multiplies the value by the arg."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value
