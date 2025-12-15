"""
Custom template filters for Dashboard
"""
from django import template
from django.template.defaultfilters import floatformat

register = template.Library()


@register.filter
def millions(value, decimals=0):
    """
    Format angka menjadi jutaan (dibagi 1.000.000)
    Contoh: 614.000.000 -> 614
    """
    try:
        if value is None or value == '' or value == '-':
            return '-'
        num = float(value)
        result = num / 1000000
        return floatformat(result, decimals)
    except (ValueError, TypeError):
        return '-'


@register.filter
def millions_with_comma(value, decimals=0):
    """
    Format angka menjadi jutaan dengan separator koma
    Contoh: 614000000000 -> 614,000
    """
    try:
        if value is None or value == '' or value == '-':
            return '-'
        num = float(value)
        result = num / 1000000
        formatted = floatformat(result, decimals)
        # Add thousand separator
        parts = str(formatted).split('.')
        parts[0] = '{:,}'.format(int(parts[0].replace(',', '').replace(' ', '')))
        return '.'.join(parts) if len(parts) > 1 else parts[0]
    except (ValueError, TypeError):
        return '-'


@register.filter
def percentage(value, decimals=1):
    """
    Format angka sebagai persentase
    """
    try:
        if value is None or value == '' or value == '-':
            return '-'
        num = float(value)
        return f"{floatformat(num, decimals)}%"
    except (ValueError, TypeError):
        return '-'


@register.filter
def abs_value(value):
    """
    Return absolute value
    """
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return value


@register.filter
def format_number(value, decimals=0):
    """
    Format number divided by 1 million with thousand separator
    Example: 620,546,000,000 -> 620,546
    """
    try:
        if value is None or value == '' or value == '-':
            return '-'
        num = float(value)
        # Divide by 1 million
        result = num / 1000000
        formatted = floatformat(result, decimals)
        parts = str(formatted).split('.')
        parts[0] = '{:,}'.format(int(parts[0].replace(',', '').replace(' ', '')))
        return '.'.join(parts) if len(parts) > 1 else parts[0]
    except (ValueError, TypeError):
        return '-'
