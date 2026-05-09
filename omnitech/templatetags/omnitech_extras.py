"""
Custom template filters for OmniTech
"""
from django import template

register = template.Library()

@register.filter
def clp_currency(value):
    if value is None:
        return "0"
    try:
        num = int(float(value))
    except (ValueError, TypeError):
        return "0"
    return f"{num:,}".replace(",", ".")

@register.filter
def clp_price(value):
    return f"${clp_currency(value)}"

@register.filter
def class_name(value):
    return value.__class__.__name__ if value else ''