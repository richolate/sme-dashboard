"""
Utility functions untuk Dashboard Performance Highlights SME
"""

from datetime import datetime, timedelta
from django.db.models import Sum, Count, Avg, Q


def format_currency(amount):
    """
    Format angka menjadi format Rupiah
    
    Args:
        amount: Decimal or int
    
    Returns:
        str: Formatted currency (e.g., "Rp 1.000.000")
    """
    if amount is None:
        return "Rp 0"
    
    try:
        amount = float(amount)
        return f"Rp {amount:,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return "Rp 0"


def format_number(number):
    """
    Format angka dengan separator titik
    
    Args:
        number: int or float
    
    Returns:
        str: Formatted number (e.g., "1.000.000")
    """
    if number is None:
        return "0"
    
    try:
        number = float(number)
        return f"{number:,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return "0"


def format_percentage(value, total, decimals=2):
    """
    Hitung dan format persentase
    
    Args:
        value: Nilai
        total: Total nilai
        decimals: Jumlah desimal
    
    Returns:
        str: Formatted percentage (e.g., "25.50%")
    """
    if not total or total == 0:
        return "0%"
    
    try:
        percentage = (float(value) / float(total)) * 100
        return f"{percentage:.{decimals}f}%"
    except (ValueError, TypeError, ZeroDivisionError):
        return "0%"


def get_date_range(period='today'):
    """
    Get date range untuk filtering
    
    Args:
        period: 'today', 'yesterday', 'this_week', 'this_month', 'this_year', 'last_30_days'
    
    Returns:
        tuple: (start_date, end_date)
    """
    today = datetime.now().date()
    
    if period == 'today':
        return today, today
    
    elif period == 'yesterday':
        yesterday = today - timedelta(days=1)
        return yesterday, yesterday
    
    elif period == 'this_week':
        start = today - timedelta(days=today.weekday())
        return start, today
    
    elif period == 'this_month':
        start = today.replace(day=1)
        return start, today
    
    elif period == 'this_year':
        start = today.replace(month=1, day=1)
        return start, today
    
    elif period == 'last_30_days':
        start = today - timedelta(days=30)
        return start, today
    
    elif period == 'last_7_days':
        start = today - timedelta(days=7)
        return start, today
    
    else:
        return today, today


def calculate_growth_rate(current, previous):
    """
    Hitung growth rate (pertumbuhan)
    
    Args:
        current: Nilai saat ini
        previous: Nilai sebelumnya
    
    Returns:
        dict: {'value': growth_rate, 'direction': 'up'/'down'/'same'}
    """
    if not previous or previous == 0:
        return {'value': 0, 'direction': 'same'}
    
    try:
        current = float(current)
        previous = float(previous)
        growth = ((current - previous) / previous) * 100
        
        if growth > 0:
            direction = 'up'
        elif growth < 0:
            direction = 'down'
        else:
            direction = 'same'
        
        return {
            'value': round(growth, 2),
            'direction': direction
        }
    except (ValueError, TypeError, ZeroDivisionError):
        return {'value': 0, 'direction': 'same'}


def aggregate_by_period(queryset, date_field, period='day'):
    """
    Aggregate data berdasarkan periode
    
    Args:
        queryset: Django QuerySet
        date_field: Nama field tanggal
        period: 'day', 'week', 'month', 'year'
    
    Returns:
        QuerySet: Aggregated data
    """
    from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
    
    trunc_functions = {
        'day': TruncDay,
        'week': TruncWeek,
        'month': TruncMonth,
        'year': TruncYear,
    }
    
    trunc_func = trunc_functions.get(period, TruncDay)
    
    return queryset.annotate(
        period=trunc_func(date_field)
    ).values('period').annotate(
        total=Count('id'),
        sum_plafon=Sum('plafon')
    ).order_by('period')


def validate_date_range(start_date, end_date):
    """
    Validasi date range
    
    Args:
        start_date: Tanggal mulai
        end_date: Tanggal akhir
    
    Returns:
        dict: {'valid': True/False, 'message': '...'}
    """
    try:
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if start_date > end_date:
            return {
                'valid': False,
                'message': 'Tanggal mulai tidak boleh lebih besar dari tanggal akhir'
            }
        
        # Check if range is too large (e.g., > 1 year)
        if (end_date - start_date).days > 365:
            return {
                'valid': False,
                'message': 'Rentang tanggal terlalu besar (maksimal 1 tahun)'
            }
        
        return {'valid': True, 'message': ''}
    
    except (ValueError, TypeError) as e:
        return {
            'valid': False,
            'message': f'Format tanggal tidak valid: {str(e)}'
        }


def get_status_badge_class(status):
    """
    Get Bootstrap badge class berdasarkan status
    
    Args:
        status: Status string
    
    Returns:
        str: Bootstrap class
    """
    status_mapping = {
        'active': 'bg-success',
        'paid off': 'bg-primary',
        'overdue': 'bg-danger',
        'restructured': 'bg-warning',
        'pending': 'bg-secondary',
        'completed': 'bg-success',
        'processing': 'bg-info',
        'failed': 'bg-danger',
    }
    
    return status_mapping.get(status.lower(), 'bg-secondary')


def chunk_queryset(queryset, chunk_size=1000):
    """
    Split queryset menjadi chunks untuk processing
    Berguna untuk processing data besar
    
    Args:
        queryset: Django QuerySet
        chunk_size: Ukuran setiap chunk
    
    Yields:
        QuerySet: Chunk of queryset
    """
    count = queryset.count()
    for i in range(0, count, chunk_size):
        yield queryset[i:i + chunk_size]


def sanitize_filename(filename):
    """
    Sanitize filename untuk keamanan
    
    Args:
        filename: Original filename
    
    Returns:
        str: Safe filename
    """
    import re
    import os
    
    # Get file extension
    name, ext = os.path.splitext(filename)
    
    # Remove special characters
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[-\s]+', '-', name)
    
    # Limit length
    name = name[:100]
    
    # Add timestamp untuk uniqueness
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    return f"{name}_{timestamp}{ext}"


def export_to_csv(queryset, fields, filename='export.csv'):
    """
    Export queryset ke CSV
    
    Args:
        queryset: Django QuerySet
        fields: List of field names
        filename: Output filename
    
    Returns:
        HttpResponse: CSV file response
    """
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow(fields)
    
    # Write data
    for obj in queryset:
        row = [getattr(obj, field) for field in fields]
        writer.writerow(row)
    
    return response


def get_business_days(start_date, end_date):
    """
    Hitung jumlah hari kerja antara dua tanggal
    
    Args:
        start_date: Tanggal mulai
        end_date: Tanggal akhir
    
    Returns:
        int: Jumlah hari kerja
    """
    from datetime import timedelta
    
    business_days = 0
    current_date = start_date
    
    while current_date <= end_date:
        # 0 = Monday, 6 = Sunday
        if current_date.weekday() < 5:  # Monday to Friday
            business_days += 1
        current_date += timedelta(days=1)
    
    return business_days


def calculate_aging(date_from, date_to=None):
    """
    Calculate aging (umur) dalam hari
    
    Args:
        date_from: Tanggal awal
        date_to: Tanggal akhir (default: today)
    
    Returns:
        int: Jumlah hari
    """
    if date_to is None:
        date_to = datetime.now().date()
    
    if isinstance(date_from, str):
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
    
    if isinstance(date_to, str):
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    
    return (date_to - date_from).days


def get_color_palette():
    """
    Get color palette untuk charts
    
    Returns:
        dict: Color schemes
    """
    return {
        'primary': [
            '#0d6efd', '#6610f2', '#6f42c1', '#d63384', '#dc3545',
            '#fd7e14', '#ffc107', '#28a745', '#20c997', '#17a2b8'
        ],
        'pastel': [
            '#FFB3BA', '#FFDFBA', '#FFFFBA', '#BAFFC9', '#BAE1FF',
            '#E0BBE4', '#FFDFD3', '#D4F0F0', '#FCE1E4', '#F0E8D8'
        ],
        'professional': [
            '#2E4053', '#5D6D7E', '#85929E', '#ABB2B9', '#D5D8DC',
            '#1A5490', '#2874A6', '#5DADE2', '#85C1E2', '#AED6F1'
        ]
    }
