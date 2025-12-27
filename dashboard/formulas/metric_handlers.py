"""
Metric View Handlers
Separate handlers for each metric type (OS, DPK, NPL, etc.)
"""

from datetime import datetime
from .table_builder import build_metric_tables


# ============================================================================
# Helper Functions
# ============================================================================

def get_komitmen_label(selected_date):
    """Generate dynamic komitmen label based on selected date."""
    month_names = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }
    return f"{month_names[selected_date.month]}'{str(selected_date.year)[2:]}"


# ============================================================================
# OS (Outstanding) Handler
# ============================================================================

def handle_os_view(request, segment_filter='SMALL'):
    """
    Handle OS (Outstanding) metric view.
    
    Args:
        request: Django request object
        segment_filter: Segment to filter ('SMALL', 'MEDIUM', 'CC', 'KUR', 'SMALL NCC')
    
    Returns:
        dict: Context data for template
    """
    # Get selected date from request or use today
    selected_date_str = request.GET.get('selected_date', datetime.now().strftime('%Y-%m-%d'))
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = datetime.now().date()
    
    # Build tables using the generic builder
    table_data = build_metric_tables(
        selected_date=selected_date,
        segment_filter=segment_filter,
        metric_field='os'
    )
    
    # Prepare context
    context = {
        'show_os_tables': True,
        'tables': table_data,
        'selected_date_str': selected_date.strftime('%Y-%m-%d'),
        'date_columns': table_data['date_columns'],
        'komitmen_label': get_komitmen_label(selected_date),
        'dtd_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['D']['date'].strftime('%d %b')}",
        'mom_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['B']['date'].strftime('%d %b')}",
        'mtd_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['C']['date'].strftime('%d %b')}",
        'ytd_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['A']['date'].strftime('%d %b')}",
    }
    
    return context


# ============================================================================
# DPK (Dana Pihak Ketiga) Handler
# ============================================================================

def handle_dpk_view(request, segment_filter='SMALL'):
    """
    Handle DPK (Dana Pihak Ketiga) metric view.
    DPK uses SML formula: SML = DPK + (Lancar if kol_adk == '2')
    Structure identical to OS SMALL, only the metric field differs.
    
    Args:
        request: Django request object
        segment_filter: Segment to filter
    
    Returns:
        dict: Context data for template
    """
    # Get selected date
    selected_date_str = request.GET.get('selected_date', datetime.now().strftime('%Y-%m-%d'))
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = datetime.now().date()
    
    # Build tables for DPK metric (uses 'sml' field from calculations.py)
    # SML = val_dpk + (val_lancar if kol_adk='2')
    # Table structure same as OS SMALL, only metric_field='dpk' maps to 'sml'
    table_data = build_metric_tables(
        selected_date=selected_date,
        segment_filter=segment_filter,
        metric_field='dpk'  # Will be mapped to 'sml' field in table_builder
    )
    
    # Format komitmen header (dynamic month label)
    month_names = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }
    komitmen_label = f"{month_names[selected_date.month]}'{str(selected_date.year)[2:]}"
    
    context = {
        'show_os_tables': True,
        'metric_type': 'dpk',  # For conditional color logic in template (inverse colors)
        'tables': table_data,
        'selected_date_str': selected_date.strftime('%Y-%m-%d'),
        'date_columns': table_data['date_columns'],
        'komitmen_label': komitmen_label,
        'dtd_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['D']['date'].strftime('%d %b')}",
        'mom_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['B']['date'].strftime('%d %b')}",
        'mtd_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['C']['date'].strftime('%d %b')}",
        'ytd_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['A']['date'].strftime('%d %b')}",
    }
    
    return context


# ============================================================================
# %DPK (Percentage DPK) Handler
# ============================================================================

def handle_dpk_pct_view(request, segment_filter='SMALL'):
    """
    Handle %DPK (Percentage DPK to OS) metric view.
    Formula: (DPK / OS) * 100
    
    Args:
        request: Django request object
        segment_filter: Segment to filter
    
    Returns:
        dict: Context data for template
    """
    # Get selected date
    selected_date_str = request.GET.get('selected_date', datetime.now().strftime('%Y-%m-%d'))
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = datetime.now().date()
    
    # Build tables for %DPK metric (special calculation)
    # This will need custom logic in table_builder to calculate percentage
    table_data = build_metric_tables(
        selected_date=selected_date,
        segment_filter=segment_filter,
        metric_field='dpk_pct'  # Special field for percentage
    )
    
    # Format komitmen header (dynamic month label)
    month_names = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }
    komitmen_label = f"{month_names[selected_date.month]}'{str(selected_date.year)[2:]}"
    
    context = {
        'show_os_tables': True,
        'metric_type': 'dpk_pct',  # For percentage formatting and inverse color logic
        'tables': table_data,
        'selected_date_str': selected_date.strftime('%Y-%m-%d'),
        'date_columns': table_data['date_columns'],
        'komitmen_label': komitmen_label,
        'dtd_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['D']['date'].strftime('%d %b')}",
        'mom_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['B']['date'].strftime('%d %b')}",
        'mtd_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['C']['date'].strftime('%d %b')}",
        'ytd_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['A']['date'].strftime('%d %b')}",
    }
    
    return context


# ============================================================================
# NPL (Non-Performing Loan) Handler
# ============================================================================

def handle_npl_view(request, segment_filter='SMALL'):
    """
    Handle NPL (Non-Performing Loan) metric view.
    NPL uses formula: NPL = KL + D + M (from calculations.py)
    Structure identical to OS SMALL, only the metric field differs.
    
    Args:
        request: Django request object
        segment_filter: Segment to filter
    
    Returns:
        dict: Context data for template
    """
    selected_date_str = request.GET.get('selected_date', datetime.now().strftime('%Y-%m-%d'))
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = datetime.now().date()
    
    # Build tables for NPL metric (uses 'npl' field from calculations.py)
    # NPL = val_kl + val_d + val_m
    # Table structure same as OS SMALL, only metric_field='npl'
    table_data = build_metric_tables(
        selected_date=selected_date,
        segment_filter=segment_filter,
        metric_field='npl'
    )
    
    context = {
        'show_os_tables': True,
        'metric_type': 'npl',  # For conditional color logic in template (inverse colors)
        'tables': table_data,
        'selected_date_str': selected_date.strftime('%Y-%m-%d'),
        'date_columns': table_data['date_columns'],
        'komitmen_label': get_komitmen_label(selected_date),
        'dtd_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['D']['date'].strftime('%d %b')}",
        'mom_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['B']['date'].strftime('%d %b')}",
        'mtd_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['C']['date'].strftime('%d %b')}",
        'ytd_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['A']['date'].strftime('%d %b')}",
    }
    
    return context


# ============================================================================
# %NPL (Percentage NPL) Handler
# ============================================================================

def handle_npl_pct_view(request, segment_filter='SMALL'):
    """
    Handle %NPL (NPL Ratio) metric view.
    Formula: (NPL / OS) * 100
    
    Args:
        request: Django request object
        segment_filter: Segment to filter
    
    Returns:
        dict: Context data for template
    """
    selected_date_str = request.GET.get('selected_date', datetime.now().strftime('%Y-%m-%d'))
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = datetime.now().date()
    
    table_data = build_metric_tables(
        selected_date=selected_date,
        segment_filter=segment_filter,
        metric_field='npl_pct'
    )
    
    context = {
        'show_os_tables': True,
        'metric_type': 'npl_pct',  # For percentage formatting and inverse color logic
        'tables': table_data,
        'selected_date_str': selected_date.strftime('%Y-%m-%d'),
        'date_columns': table_data['date_columns'],
        'komitmen_label': get_komitmen_label(selected_date),
        'dtd_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['D']['date'].strftime('%d %b')}",
        'mom_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['B']['date'].strftime('%d %b')}",
        'mtd_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['C']['date'].strftime('%d %b')}",
        'ytd_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['A']['date'].strftime('%d %b')}",
    }
    
    return context


# ============================================================================
# LAR (Loan at Risk) Handler
# ============================================================================

def handle_lar_view(request, segment_filter='SMALL'):
    """
    Handle LAR (Loan at Risk) metric view.
    LAR uses formula: LAR = SML + NPL + LR (from calculations.py)
    Structure identical to OS SMALL, only the metric field differs.
    
    Args:
        request: Django request object
        segment_filter: Segment to filter
    
    Returns:
        dict: Context data for template
    """
    selected_date_str = request.GET.get('selected_date', datetime.now().strftime('%Y-%m-%d'))
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = datetime.now().date()
    
    # Build tables for LAR metric (uses 'lar' field from calculations.py)
    # LAR = sml + npl + lr
    # Table structure same as OS SMALL, only metric_field='lar'
    table_data = build_metric_tables(
        selected_date=selected_date,
        segment_filter=segment_filter,
        metric_field='lar'
    )
    
    context = {
        'show_os_tables': True,
        'metric_type': 'lar',  # For conditional color logic in template (inverse colors)
        'tables': table_data,
        'selected_date_str': selected_date.strftime('%Y-%m-%d'),
        'date_columns': table_data['date_columns'],
        'komitmen_label': get_komitmen_label(selected_date),
        'dtd_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['D']['date'].strftime('%d %b')}",
        'mom_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['B']['date'].strftime('%d %b')}",
        'mtd_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['C']['date'].strftime('%d %b')}",
        'ytd_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['A']['date'].strftime('%d %b')}",
    }
    
    return context


# ============================================================================
# NSB (Nasabah/Customer Count) Handler
# ============================================================================

def handle_nsb_view(request, segment_filter='SMALL'):
    """
    Handle NSB (Nasabah/Customer Count) metric view.
    
    Args:
        request: Django request object
        segment_filter: Segment to filter
    
    Returns:
        dict: Context data for template
    """
    selected_date_str = request.GET.get('selected_date', datetime.now().strftime('%Y-%m-%d'))
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = datetime.now().date()
    
    # NSB uses count instead of sum
    table_data = build_metric_tables(
        selected_date=selected_date,
        segment_filter=segment_filter,
        metric_field='nsb'  # Special handling for count
    )
    
    context = {
        'show_os_tables': True,
        'tables': table_data,
        'selected_date_str': selected_date.strftime('%Y-%m-%d'),
        'date_columns': table_data['date_columns'],
        'komitmen_label': get_komitmen_label(selected_date),
        'dtd_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['D']['date'].strftime('%d %b')}",
        'mom_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['B']['date'].strftime('%d %b')}",
        'mtd_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['C']['date'].strftime('%d %b')}",
        'ytd_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['A']['date'].strftime('%d %b')}",
    }
    
    return context


# ============================================================================
# LR (Loan Restructured) Handler
# ============================================================================

def handle_lr_view(request, segment_filter='SMALL'):
    """
    Handle LR (Loan Restructured) metric view.
    LR uses formula: LR = Lancar if (kol_adk == '1' AND flag_restruk == 'Y')
    Structure identical to OS SMALL, only the metric field differs.
    
    Args:
        request: Django request object
        segment_filter: Segment to filter
    
    Returns:
        dict: Context data for template
    """
    selected_date_str = request.GET.get('selected_date', datetime.now().strftime('%Y-%m-%d'))
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = datetime.now().date()
    
    # Build tables for LR metric (uses 'lr' field from calculations.py)
    # LR = val_lancar if (kol_adk='1' AND flag_restruk='Y')
    # Table structure same as OS SMALL, only metric_field='lr'
    table_data = build_metric_tables(
        selected_date=selected_date,
        segment_filter=segment_filter,
        metric_field='lr'
    )
    
    context = {
        'show_os_tables': True,
        'metric_type': 'lr',  # For conditional color logic in template (inverse colors)
        'tables': table_data,
        'selected_date_str': selected_date.strftime('%Y-%m-%d'),
        'date_columns': table_data['date_columns'],
        'komitmen_label': get_komitmen_label(selected_date),
        'dtd_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['D']['date'].strftime('%d %b')}",
        'mom_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['B']['date'].strftime('%d %b')}",
        'mtd_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['C']['date'].strftime('%d %b')}",
        'ytd_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['A']['date'].strftime('%d %b')}",
    }
    
    return context


# ============================================================================
# NSB (Nasabah/Customer Count) Handler
# ============================================================================

def handle_nsb_view(request, segment_filter='SMALL'):
    """
    Handle NSB (Nasabah) metric view.
    NSB counts unique customers (distinct CIFNO) for the segment.
    Structure identical to OS SMALL, but counts customers instead of summing amounts.
    
    Args:
        request: Django request object
        segment_filter: Segment to filter
    
    Returns:
        dict: Context data for template
    """
    # Get selected date
    selected_date_str = request.GET.get('selected_date', datetime.now().strftime('%Y-%m-%d'))
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = datetime.now().date()
    
    # Build tables for NSB metric (counts distinct CIFNO)
    # Uses 'nsb' as metric_field which will trigger customer counting in table_builder
    table_data = build_metric_tables(
        selected_date=selected_date,
        segment_filter=segment_filter,
        metric_field='nsb'  # Special field for customer counting
    )
    
    context = {
        'show_os_tables': True,
        'metric_type': 'nsb',  # NSB uses normal colors (more customers = positive)
        'tables': table_data,
        'selected_date_str': selected_date.strftime('%Y-%m-%d'),
        'date_columns': table_data['date_columns'],
        'komitmen_label': get_komitmen_label(selected_date),
        'dtd_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['D']['date'].strftime('%d %b')}",
        'mom_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['B']['date'].strftime('%d %b')}",
        'mtd_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['C']['date'].strftime('%d %b')}",
        'ytd_header': f"{table_data['date_columns']['E']['date'].strftime('%d %b')} - {table_data['date_columns']['A']['date'].strftime('%d %b')}",
    }
    
    return context


# ============================================================================
# Metric Handler Mapper
# ============================================================================

METRIC_HANDLERS = {
    'os': handle_os_view,
    'dpk': handle_dpk_view,
    'dpk-pct': handle_dpk_pct_view,
    'npl': handle_npl_view,
    'npl-pct': handle_npl_pct_view,
    'lar': handle_lar_view,
    'nsb': handle_nsb_view,
    'lr': handle_lr_view,
}


def get_metric_handler(metric_type):
    """
    Get the appropriate handler for a metric type.
    
    Args:
        metric_type: Type of metric ('os', 'dpk', 'npl', etc.)
    
    Returns:
        function: Handler function for the metric
    """
    return METRIC_HANDLERS.get(metric_type, handle_os_view)
