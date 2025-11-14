from django.http import Http404
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .navigation import METRIC_PAGES


@login_required
def home_view(request):
    """
    Halaman utama dashboard
    """
    context = {
        'user': request.user,
    }
    return render(request, 'dashboard/home.html', context)


@login_required
def dashboard_os_view(request):
    """
    Dashboard OS
    """
    context = {
        'page_title': 'Dashboard OS',
    }
    return render(request, 'dashboard/dashboard_os.html', context)


@login_required
def dashboard_summary_view(request):
    """
    Dashboard Summary dengan sub-tabs
    """
    # Default tab
    active_tab = request.GET.get('tab', 'medium_only')
    
    context = {
        'page_title': 'Dashboard Summary',
        'active_tab': active_tab,
    }
    return render(request, 'dashboard/dashboard_summary.html', context)


@login_required
def dashboard_grafik_harian_view(request):
    """
    Dashboard Grafik Harian
    """
    context = {
        'page_title': 'Dashboard Grafik Harian',
    }
    return render(request, 'dashboard/dashboard_grafik_harian.html', context)


@login_required
def metric_page_view(request, slug):
    """Generic placeholder page for segmented dashboard menus."""

    page = METRIC_PAGES.get(slug)
    if not page:
        raise Http404('Halaman tidak ditemukan.')

    context = {
        'page_title': page.title,
        'section': page.section,
        'tables': page.tables,
        'description': page.description,
    }
    return render(request, 'dashboard/metric_page.html', context)
