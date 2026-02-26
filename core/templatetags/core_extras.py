from django import template

register = template.Library()


@register.filter
def split(value, arg):
    """Split a string by `arg`. Usage: "a,b,c"|split:"," """
    return value.split(arg)


@register.filter
def first(value):
    """Return the first element of a list."""
    try:
        return value[0]
    except (IndexError, TypeError):
        return ''


@register.filter
def last(value):
    """Return the last element of a list."""
    try:
        return value[-1]
    except (IndexError, TypeError):
        return ''
