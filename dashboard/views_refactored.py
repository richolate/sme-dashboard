# Add these new view functions to views.py after the metric_page function

def small_os_view(request):
    """
    OS SMALL - Outstanding balance for SMALL segment.
    REFACTORED: Uses modular metric_handlers instead of 370+ lines of inline code.
    """
    from .formulas.metric_handlers import handle_os_view
    from .navigation import build_menu
    
    context = {
        'menu': build_menu('small-os'),
        'active_slug': 'small-os',
    }
    context.update(handle_os_view(request, segment_filter='SMALL'))
    
    return render(request, 'dashboard/metric_page.html', context)


def small_dpk_view(request):
    """
    DPK SMALL - Dana Pihak Ketiga for SMALL segment.
    Filtered by kol_adk='2' (Kolektibilitas DPK).
    """
    from .formulas.metric_handlers import handle_dpk_view
    from .navigation import build_menu
    
    context = {
        'menu': build_menu('small-dpk'),
        'active_slug': 'small-dpk',
    }
    context.update(handle_dpk_view(request, segment_filter='SMALL'))
    
    return render(request, 'dashboard/metric_page.html', context)
