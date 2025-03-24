from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiply the value and arg together."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''
