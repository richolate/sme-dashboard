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


@register.filter
def format_number_parentheses(value, decimals=0):
    """
    Format number divided by 1 million with thousand separator
    Negative numbers shown with parentheses instead of minus sign
    Example: -620,546,000,000 -> (620,546)
    Example: 620,546,000,000 -> 620,546
    """
    try:
        if value is None or value == '' or value == '-':
            return '-'
        num = float(value)
        # Divide by 1 million
        result = num / 1000000
        
        # Check if negative
        is_negative = result < 0
        result = abs(result)
        
        formatted = floatformat(result, decimals)
        parts = str(formatted).split('.')
        parts[0] = '{:,}'.format(int(parts[0].replace(',', '').replace(' ', '')))
        final_number = '.'.join(parts) if len(parts) > 1 else parts[0]
        
        # Return with parentheses if negative
        if is_negative:
            return f'({final_number})'
        return final_number
    except (ValueError, TypeError):
        return '-'


@register.filter
def format_integer(value, decimals=0):
    """
    Format integer with thousand separator WITHOUT dividing by 1 million
    Used for counts like NSB (customer count)
    Example: 1234 -> 1,234
    Example: 5678901 -> 5,678,901
    """
    try:
        if value is None or value == '' or value == '-':
            return '-'
        num = int(float(value))
        return '{:,}'.format(num)
    except (ValueError, TypeError):
        return '-'


@register.filter
def format_integer_parentheses(value, decimals=0):
    """
    Format integer with thousand separator WITHOUT dividing by 1 million
    Negative numbers shown with parentheses instead of minus sign
    Used for counts like NSB (customer count)
    Example: -1234 -> (1,234)
    Example: 5678 -> 5,678
    """
    try:
        if value is None or value == '' or value == '-':
            return '-'
        num = int(float(value))
        
        # Check if negative
        is_negative = num < 0
        num = abs(num)
        
        formatted = '{:,}'.format(num)
        
        # Return with parentheses if negative
        if is_negative:
            return f'({formatted})'
        return formatted
    except (ValueError, TypeError):
        return '-'
