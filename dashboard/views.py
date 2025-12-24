from django.http import Http404
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.core.serializers.json import DjangoJSONEncoder
import json
from .models import LW321
from .formulas import annotate_metrics, get_segment_annotation
from .navigation import METRIC_PAGES
from datetime import datetime
from django.db.models import DateField, Value, F
from django.db.models.functions import Cast, Concat, Substr
import math

def get_quarter(date_obj):
    return math.ceil(date_obj.month / 3)

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
    
    # Check if database has data
    has_data = LW321.objects.exists()
    if not has_data:
        context['no_data'] = True
        return render(request, 'dashboard/metric_page.html', context)

    # =================================================================================
    # SECTION: Timeseries OS Logic (Grouped by Month-Year)
    # NOTE: OS diambil dari tanggal AKHIR BULAN saja (bukan sum seluruh tanggal)
    #       Contoh: 31 Oktober 2025, 30 November 2025, 31 Desember 2025
    # =================================================================================
    if slug == 'timeseries-os':
        # 1. Base Query & Annotations
        qs = LW321.objects.all()
        qs = qs.annotate(segment=get_segment_annotation())
        qs = annotate_metrics(qs)

        # 2. Get Filter Options (Distinct Kanca)
        kanca_list = LW321.objects.values_list('kanca', flat=True).distinct().order_by('kanca')

        # 3. Handle Filters (Multi-select)
        selected_segments = request.GET.getlist('segment')
        selected_kancas = request.GET.getlist('kanca')

        if not selected_segments:
            selected_segments = ['ALL']
        if not selected_kancas:
            selected_kancas = ['ALL']

        if 'ALL' not in selected_segments:
            qs = qs.filter(segment__in=selected_segments)

        if 'ALL' not in selected_kancas:
            qs = qs.filter(kanca__in=selected_kancas)

        # 4. Group by MONTH & YEAR, lalu ambil hanya tanggal AKHIR BULAN
        from django.db.models.functions import ExtractYear, ExtractMonth, ExtractDay
        from django.db.models import Max

        # Step 4a: Konversi periode ke date dan extract year, month, day
        qs_with_date = qs.annotate(
            # Ubah DD/MM/YYYY → YYYY-MM-DD
            periode_iso=Concat(
                Substr('periode', 7, 4),  # YYYY
                Value('-'),
                Substr('periode', 4, 2),  # MM
                Value('-'),
                Substr('periode', 1, 2),  # DD
            ),
        ).annotate(
            periode_date=Cast('periode_iso', output_field=DateField())
        ).annotate(
            year=ExtractYear('periode_date'),
            month=ExtractMonth('periode_date'),
            day=ExtractDay('periode_date'),
        )

        # Step 4b: Cari tanggal maksimum (akhir bulan) per year-month
        max_days = (
            qs_with_date
            .values('year', 'month')
            .annotate(max_day=Max('day'))
            .order_by('year', 'month')
        )

        # Step 4c: Buat list of (year, month, max_day) untuk filter
        end_of_month_dates = []
        for row in max_days:
            end_of_month_dates.append({
                'year': row['year'],
                'month': row['month'],
                'day': row['max_day'],
            })

        # Step 4d: Filter hanya data yang ada di tanggal akhir bulan, lalu sum OS
        from django.db.models import Q

        labels = []
        data_values = []

        for eom in end_of_month_dates:
            yr = eom['year']
            mo = eom['month']
            dy = eom['day']

            # Filter data hanya untuk tanggal akhir bulan ini
            eom_qs = qs_with_date.filter(year=yr, month=mo, day=dy)
            total_os = eom_qs.aggregate(total=Sum('os'))['total'] or 0

            # Format label
            try:
                dt = datetime(yr, mo, dy)
                month_name = dt.strftime('%B')   # January, February, ...
                label = f"{month_name} {yr}"
            except Exception:
                label = f"{mo}-{yr}"

            labels.append(label)
            data_values.append(float(total_os))

        chart_data = {
            'labels': labels,
            'datasets': [{
                'label': 'Outstanding (OS)',
                'data': data_values,
                'backgroundColor': 'rgba(13, 110, 253, 0.7)',
                'borderColor': 'rgba(13, 110, 253, 1)',
                'borderWidth': 1,
            }]
        }

        # 5. Context
        context.update({
            'show_chart': True,
            'chart_data_json': json.dumps(chart_data, cls=DjangoJSONEncoder),
            'filters': {
                'segments': ['KUR', 'CC', 'SMALL', 'MEDIUM'],
                'kancas': list(kanca_list),
                'selected_segments': selected_segments,
                'selected_kancas': selected_kancas,
            }
        })
    # =================================================================================
    # END SECTION: Timeseries OS Logic
    # =================================================================================

    # =================================================================================
    # SECTION: Timeseries OS DPK NPL LAR Logic (Stacked Bar Chart)
    # NOTE: Data diambil dari tanggal AKHIR BULAN saja (sama seperti Timeseries OS)
    #       Metrics: OS, DPK, NPL, LAR (Stacked Vertical Bar Chart)
    # =================================================================================
    if slug == 'timeseries-os-dpk-npl-lar':
        # 1. Base Query & Annotations
        qs = LW321.objects.all()
        qs = qs.annotate(segment=get_segment_annotation())
        qs = annotate_metrics(qs)

        # 2. Get Filter Options (Distinct Kanca)
        kanca_list = LW321.objects.values_list('kanca', flat=True).distinct().order_by('kanca')

        # 3. Handle Filters (Multi-select)
        selected_segments = request.GET.getlist('segment')
        selected_kancas = request.GET.getlist('kanca')

        if not selected_segments:
            selected_segments = ['ALL']
        if not selected_kancas:
            selected_kancas = ['ALL']

        if 'ALL' not in selected_segments:
            qs = qs.filter(segment__in=selected_segments)

        if 'ALL' not in selected_kancas:
            qs = qs.filter(kanca__in=selected_kancas)

        # 4. Group by MONTH & YEAR, lalu ambil hanya tanggal AKHIR BULAN
        from django.db.models.functions import ExtractYear, ExtractMonth, ExtractDay
        from django.db.models import Max

        # Step 4a: Konversi periode ke date dan extract year, month, day
        qs_with_date = qs.annotate(
            # Ubah DD/MM/YYYY → YYYY-MM-DD
            periode_iso=Concat(
                Substr('periode', 7, 4),  # YYYY
                Value('-'),
                Substr('periode', 4, 2),  # MM
                Value('-'),
                Substr('periode', 1, 2),  # DD
            ),
        ).annotate(
            periode_date=Cast('periode_iso', output_field=DateField())
        ).annotate(
            year=ExtractYear('periode_date'),
            month=ExtractMonth('periode_date'),
            day=ExtractDay('periode_date'),
        )

        # Step 4b: Cari tanggal maksimum (akhir bulan) per year-month
        max_days = (
            qs_with_date
            .values('year', 'month')
            .annotate(max_day=Max('day'))
            .order_by('year', 'month')
        )

        # Step 4c: Buat list of (year, month, max_day) untuk filter
        end_of_month_dates = []
        for row in max_days:
            end_of_month_dates.append({
                'year': row['year'],
                'month': row['month'],
                'day': row['max_day'],
            })

        # Step 4d: Filter hanya data yang ada di tanggal akhir bulan, lalu sum metrics
        labels = []
        os_values = []
        dpk_values = []
        npl_values = []
        lar_values = []

        for eom in end_of_month_dates:
            yr = eom['year']
            mo = eom['month']
            dy = eom['day']

            # Filter data hanya untuk tanggal akhir bulan ini
            eom_qs = qs_with_date.filter(year=yr, month=mo, day=dy)
            
            # Aggregate semua metrics
            totals = eom_qs.aggregate(
                total_os=Sum('os'),
                total_dpk=Sum('sml'),  # SML = DPK based on formula
                total_npl=Sum('npl'),
                total_lar=Sum('lar'),
            )

            # Format label
            try:
                dt = datetime(yr, mo, dy)
                month_name = dt.strftime('%B')   # January, February, ...
                label = f"{month_name} {yr}"
            except Exception:
                label = f"{mo}-{yr}"

            labels.append(label)
            os_values.append(float(totals['total_os'] or 0))
            dpk_values.append(float(totals['total_dpk'] or 0))
            npl_values.append(float(totals['total_npl'] or 0))
            lar_values.append(float(totals['total_lar'] or 0))

        # 5. Chart Data untuk Stacked Bar Chart
        chart_data = {
            'labels': labels,
            'datasets': [
                {
                    'label': 'OS (Baki Debet)',
                    'data': os_values,
                    'backgroundColor': 'rgba(54, 162, 235, 0.8)',   # Blue
                    'borderColor': 'rgba(54, 162, 235, 1)',
                    'borderWidth': 1,
                },
                {
                    'label': 'DPK',
                    'data': dpk_values,
                    'backgroundColor': 'rgba(0, 0, 139, 0.8)',      # Dark Blue
                    'borderColor': 'rgba(0, 0, 139, 1)',
                    'borderWidth': 1,
                },
                {
                    'label': 'NPL',
                    'data': npl_values,
                    'backgroundColor': 'rgba(255, 159, 64, 0.8)',   # Orange
                    'borderColor': 'rgba(255, 159, 64, 1)',
                    'borderWidth': 1,
                },
                {
                    'label': 'LAR',
                    'data': lar_values,
                    'backgroundColor': 'rgba(153, 102, 255, 0.8)',  # Purple
                    'borderColor': 'rgba(153, 102, 255, 1)',
                    'borderWidth': 1,
                },
            ]
        }

        # 6. Context
        context.update({
            'show_stacked_chart': True,
            'chart_data_json': json.dumps(chart_data, cls=DjangoJSONEncoder),
            'filters': {
                'segments': ['KUR', 'CC', 'SMALL', 'MEDIUM'],
                'kancas': list(kanca_list),
                'selected_segments': selected_segments,
                'selected_kancas': selected_kancas,
            }
        })
    # =================================================================================
    # END SECTION: Timeseries OS DPK NPL LAR Logic
    # =================================================================================

    # =================================================================================
    # SECTION: Timeseries Baki Debit UKER (Daily Line Chart per Month)
    # NOTE: Grafik Line/Area Chart yang menampilkan OS per tanggal (1-31)
    #       dengan setiap bulan sebagai satu garis/area terpisah
    #       Tujuan: Membandingkan posisi OS harian antar bulan
    # =================================================================================
    if slug == 'timeseries-baki-debit-uker':
        from django.db.models.functions import ExtractYear, ExtractMonth, ExtractDay
        from django.db.models import Max
        
        # 1. Get available years from data
        qs_base = LW321.objects.annotate(
            periode_iso=Concat(
                Substr('periode', 7, 4),  # YYYY
                Value('-'),
                Substr('periode', 4, 2),  # MM
                Value('-'),
                Substr('periode', 1, 2),  # DD
            ),
        ).annotate(
            periode_date=Cast('periode_iso', output_field=DateField())
        ).annotate(
            year=ExtractYear('periode_date'),
            month=ExtractMonth('periode_date'),
            day=ExtractDay('periode_date'),
        )
        
        # Get distinct years
        available_years = list(qs_base.values_list('year', flat=True).distinct().order_by('year'))
        
        # Get distinct months (1-12)
        available_months = [
            {'value': 1, 'name': 'January'},
            {'value': 2, 'name': 'February'},
            {'value': 3, 'name': 'March'},
            {'value': 4, 'name': 'April'},
            {'value': 5, 'name': 'May'},
            {'value': 6, 'name': 'June'},
            {'value': 7, 'name': 'July'},
            {'value': 8, 'name': 'August'},
            {'value': 9, 'name': 'September'},
            {'value': 10, 'name': 'October'},
            {'value': 11, 'name': 'November'},
            {'value': 12, 'name': 'December'},
        ]
        
        # Get filter options
        kanca_list = LW321.objects.values_list('kanca', flat=True).distinct().order_by('kanca')
        
        # 2. Handle Filters
        selected_year = request.GET.get('year', str(available_years[-1]) if available_years else '2025')
        selected_months = request.GET.getlist('month')
        selected_segments = request.GET.getlist('segment')
        selected_kancas = request.GET.getlist('kanca')
        
        # Default: last 3-4 months if none selected
        if not selected_months:
            # Default to recent months (e.g., Aug, Sep, Oct, Nov)
            selected_months = ['8', '9', '10', '11']
        
        if not selected_segments:
            selected_segments = ['ALL']
        if not selected_kancas:
            selected_kancas = ['ALL']
        
        # 3. Build base queryset with annotations
        qs = LW321.objects.all()
        qs = qs.annotate(segment=get_segment_annotation())
        qs = annotate_metrics(qs)
        
        qs = qs.annotate(
            periode_iso=Concat(
                Substr('periode', 7, 4),
                Value('-'),
                Substr('periode', 4, 2),
                Value('-'),
                Substr('periode', 1, 2),
            ),
        ).annotate(
            periode_date=Cast('periode_iso', output_field=DateField())
        ).annotate(
            year=ExtractYear('periode_date'),
            month=ExtractMonth('periode_date'),
            day=ExtractDay('periode_date'),
        )
        
        # Apply year filter
        qs = qs.filter(year=int(selected_year))
        
        # Apply month filter
        selected_months_int = [int(m) for m in selected_months]
        qs = qs.filter(month__in=selected_months_int)
        
        # Apply segment filter
        if 'ALL' not in selected_segments:
            qs = qs.filter(segment__in=selected_segments)
        
        # Apply kanca filter
        if 'ALL' not in selected_kancas:
            qs = qs.filter(kanca__in=selected_kancas)
        
        # 4. Aggregate data: Group by month and day, sum OS
        chart_qs = (
            qs.values('month', 'day')
            .annotate(total_os=Sum('os'))
            .order_by('month', 'day')
        )
        
        # 5. Prepare data structure for chart
        # X-axis: days 1-31
        # Each month is a separate dataset/line
        
        # Month colors (matching the reference image)
        month_colors = {
            1: {'bg': 'rgba(100, 149, 237, 0.3)', 'border': 'rgba(100, 149, 237, 1)'},    # January - Cornflower Blue
            2: {'bg': 'rgba(255, 99, 132, 0.3)', 'border': 'rgba(255, 99, 132, 1)'},      # February - Pink
            3: {'bg': 'rgba(75, 192, 192, 0.3)', 'border': 'rgba(75, 192, 192, 1)'},      # March - Teal
            4: {'bg': 'rgba(255, 206, 86, 0.3)', 'border': 'rgba(255, 206, 86, 1)'},      # April - Yellow
            5: {'bg': 'rgba(153, 102, 255, 0.3)', 'border': 'rgba(153, 102, 255, 1)'},    # May - Purple
            6: {'bg': 'rgba(255, 159, 64, 0.3)', 'border': 'rgba(255, 159, 64, 1)'},      # June - Orange
            7: {'bg': 'rgba(54, 162, 235, 0.3)', 'border': 'rgba(54, 162, 235, 1)'},      # July - Blue
            8: {'bg': 'rgba(0, 0, 139, 0.3)', 'border': 'rgba(0, 0, 139, 1)'},            # August - Dark Blue
            9: {'bg': 'rgba(255, 165, 0, 0.3)', 'border': 'rgba(255, 165, 0, 1)'},        # September - Orange
            10: {'bg': 'rgba(50, 205, 50, 0.3)', 'border': 'rgba(50, 205, 50, 1)'},       # October - Lime Green
            11: {'bg': 'rgba(30, 144, 255, 0.3)', 'border': 'rgba(30, 144, 255, 1)'},     # November - Dodger Blue
            12: {'bg': 'rgba(220, 20, 60, 0.3)', 'border': 'rgba(220, 20, 60, 1)'},       # December - Crimson
        }
        
        month_names = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }
        
        # Organize data by month
        data_by_month = {}
        for row in chart_qs:
            mo = row['month']
            dy = row['day']
            os_val = float(row['total_os'] or 0)
            
            if mo not in data_by_month:
                data_by_month[mo] = {}
            data_by_month[mo][dy] = os_val
        
        # Build datasets for each month
        datasets = []
        for mo in sorted(data_by_month.keys()):
            # Create array of 31 days (None for missing days)
            day_data = []
            for d in range(1, 32):
                day_data.append(data_by_month[mo].get(d, None))
            
            colors = month_colors.get(mo, {'bg': 'rgba(128, 128, 128, 0.3)', 'border': 'rgba(128, 128, 128, 1)'})
            
            datasets.append({
                'label': month_names.get(mo, f'Month {mo}'),
                'data': day_data,
                'backgroundColor': colors['bg'],
                'borderColor': colors['border'],
                'borderWidth': 2,
                'fill': True,  # For area chart effect
                'tension': 0.3,  # Smooth curves
                'pointRadius': 3,
                'pointHoverRadius': 5,
            })
        
        # X-axis labels: 1-31
        labels = list(range(1, 32))
        
        chart_data = {
            'labels': labels,
            'datasets': datasets,
        }
        
        # 6. Context
        context.update({
            'show_daily_chart': True,
            'chart_data_json': json.dumps(chart_data, cls=DjangoJSONEncoder),
            'filters': {
                'years': available_years,
                'months': available_months,
                'segments': ['KUR', 'CC', 'SMALL', 'MEDIUM'],
                'kancas': list(kanca_list),
                'selected_year': selected_year,
                'selected_months': selected_months,
                'selected_segments': selected_segments,
                'selected_kancas': selected_kancas,
            }
        })
    # =================================================================================
    # END SECTION: Timeseries Baki Debit UKER
    # =================================================================================

    # =================================================================================
    # SECTION: Timeseries Bulanan (4 Smoothed Line Charts: SML, NPL, OS, LAR)
    # NOTE: Data diambil dari tanggal AKHIR BULAN saja
    #       X-axis: Bulan (January - December)
    #       Setiap tahun yang dipilih menjadi satu line terpisah
    #       4 Grafik: SML, NPL, Baki Debet (OS), LAR
    # =================================================================================
    if slug == 'timeseries-bulanan':
        from django.db.models.functions import ExtractYear, ExtractMonth, ExtractDay
        from django.db.models import Max
        
        # 1. Get available years from data
        qs_base = LW321.objects.annotate(
            periode_iso=Concat(
                Substr('periode', 7, 4),  # YYYY
                Value('-'),
                Substr('periode', 4, 2),  # MM
                Value('-'),
                Substr('periode', 1, 2),  # DD
            ),
        ).annotate(
            periode_date=Cast('periode_iso', output_field=DateField())
        ).annotate(
            year=ExtractYear('periode_date'),
        )
        
        # Get distinct years
        available_years = list(qs_base.values_list('year', flat=True).distinct().order_by('year'))
        
        # Get distinct months (1-12)
        available_months = [
            {'value': 1, 'name': 'January'},
            {'value': 2, 'name': 'February'},
            {'value': 3, 'name': 'March'},
            {'value': 4, 'name': 'April'},
            {'value': 5, 'name': 'May'},
            {'value': 6, 'name': 'June'},
            {'value': 7, 'name': 'July'},
            {'value': 8, 'name': 'August'},
            {'value': 9, 'name': 'September'},
            {'value': 10, 'name': 'October'},
            {'value': 11, 'name': 'November'},
            {'value': 12, 'name': 'December'},
        ]
        
        # Get filter options
        kanca_list = LW321.objects.values_list('kanca', flat=True).distinct().order_by('kanca')
        
        # 2. Handle Filters
        selected_years = request.GET.getlist('year')
        selected_months = request.GET.getlist('month')
        selected_segments = request.GET.getlist('segment')
        selected_kancas = request.GET.getlist('kanca')
        
        # Default: All years if none selected
        if not selected_years:
            selected_years = [str(y) for y in available_years]
        
        # Default: All months (1-12) if none selected
        if not selected_months:
            selected_months = [str(i) for i in range(1, 13)]
        
        if not selected_segments:
            selected_segments = ['ALL']
        if not selected_kancas:
            selected_kancas = ['ALL']
        
        # 3. Build base queryset with annotations
        qs = LW321.objects.all()
        qs = qs.annotate(segment=get_segment_annotation())
        qs = annotate_metrics(qs)
        
        qs = qs.annotate(
            periode_iso=Concat(
                Substr('periode', 7, 4),
                Value('-'),
                Substr('periode', 4, 2),
                Value('-'),
                Substr('periode', 1, 2),
            ),
        ).annotate(
            periode_date=Cast('periode_iso', output_field=DateField())
        ).annotate(
            year=ExtractYear('periode_date'),
            month=ExtractMonth('periode_date'),
            day=ExtractDay('periode_date'),
        )
        
        # Apply year filter
        selected_years_int = [int(y) for y in selected_years]
        qs = qs.filter(year__in=selected_years_int)
        
        # Apply month filter
        selected_months_int = [int(m) for m in selected_months]
        qs = qs.filter(month__in=selected_months_int)
        
        # Apply segment filter
        if 'ALL' not in selected_segments:
            qs = qs.filter(segment__in=selected_segments)
        
        # Apply kanca filter
        if 'ALL' not in selected_kancas:
            qs = qs.filter(kanca__in=selected_kancas)
        
        # 4. Get end-of-month data for each year-month combination
        max_days = (
            qs.values('year', 'month')
            .annotate(max_day=Max('day'))
            .order_by('year', 'month')
        )
        
        end_of_month_dates = []
        for row in max_days:
            end_of_month_dates.append({
                'year': row['year'],
                'month': row['month'],
                'day': row['max_day'],
            })
        
        # 5. Aggregate data for each year-month at end of month
        # Structure: {year: {month: {sml, npl, os, lar}}}
        data_by_year = {}
        
        for eom in end_of_month_dates:
            yr = eom['year']
            mo = eom['month']
            dy = eom['day']
            
            eom_qs = qs.filter(year=yr, month=mo, day=dy)
            totals = eom_qs.aggregate(
                total_sml=Sum('sml'),
                total_npl=Sum('npl'),
                total_os=Sum('os'),
                total_lar=Sum('lar'),
            )
            
            if yr not in data_by_year:
                data_by_year[yr] = {}
            
            data_by_year[yr][mo] = {
                'sml': float(totals['total_sml'] or 0),
                'npl': float(totals['total_npl'] or 0),
                'os': float(totals['total_os'] or 0),
                'lar': float(totals['total_lar'] or 0),
            }
        
        # 6. Prepare chart data for each metric
        # X-axis labels: Months (filtered)
        month_names = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }
        
        # Filter months for labels
        labels = [month_names[m] for m in sorted(selected_months_int)]
        
        # Year colors
        year_colors = {
            2023: {'bg': 'rgba(100, 149, 237, 0.3)', 'border': 'rgba(100, 149, 237, 1)'},  # Light Blue
            2024: {'bg': 'rgba(0, 0, 139, 0.3)', 'border': 'rgba(0, 0, 139, 1)'},          # Dark Blue
            2025: {'bg': 'rgba(255, 99, 71, 0.3)', 'border': 'rgba(255, 99, 71, 1)'},      # Tomato/Orange
            2026: {'bg': 'rgba(50, 205, 50, 0.3)', 'border': 'rgba(50, 205, 50, 1)'},      # Lime Green
        }
        
        def build_chart_for_metric(metric_key):
            datasets = []
            for yr in sorted(data_by_year.keys()):
                year_data = []
                for mo in sorted(selected_months_int):
                    if mo in data_by_year[yr]:
                        year_data.append(data_by_year[yr][mo].get(metric_key, None))
                    else:
                        year_data.append(None)
                
                colors = year_colors.get(yr, {'bg': 'rgba(128, 128, 128, 0.3)', 'border': 'rgba(128, 128, 128, 1)'})
                
                datasets.append({
                    'label': str(yr),
                    'data': year_data,
                    'backgroundColor': colors['bg'],
                    'borderColor': colors['border'],
                    'borderWidth': 2,
                    'fill': False,
                    'tension': 0.4,  # Smooth curves
                    'pointRadius': 4,
                    'pointHoverRadius': 6,
                })
            
            return {
                'labels': labels,
                'datasets': datasets,
            }
        
        # Build chart data for each metric
        chart_sml = build_chart_for_metric('sml')
        chart_npl = build_chart_for_metric('npl')
        chart_os = build_chart_for_metric('os')
        chart_lar = build_chart_for_metric('lar')
        
        # 7. Context
        context.update({
            'show_monthly_charts': True,
            'chart_sml_json': json.dumps(chart_sml, cls=DjangoJSONEncoder),
            'chart_npl_json': json.dumps(chart_npl, cls=DjangoJSONEncoder),
            'chart_os_json': json.dumps(chart_os, cls=DjangoJSONEncoder),
            'chart_lar_json': json.dumps(chart_lar, cls=DjangoJSONEncoder),
            'filters': {
                'years': available_years,
                'months': available_months,
                'segments': ['KUR', 'CC', 'SMALL', 'MEDIUM'],
                'kancas': list(kanca_list),
                'selected_years': selected_years,
                'selected_months': selected_months,
                'selected_segments': selected_segments,
                'selected_kancas': selected_kancas,
            }
        })
    # =================================================================================
    # END SECTION: Timeseries Bulanan
    # =================================================================================

    # =================================================================================
    # SECTION: Timeseries Harian (3 Smoothed Line Charts: LAR, NPL, SML)
    # NOTE: Data diambil secara HARIAN (semua tanggal dalam bulan yang dipilih)
    #       X-axis: Tanggal (1-31)
    #       Setiap bulan yang dipilih menjadi satu line terpisah
    #       3 Grafik: LAR, NPL, SML (stacked vertically)
    #       Filter: Mirip Timeseries Baki Debit UKER (Year radio, Month checkbox)
    # =================================================================================
    if slug == 'timeseries-harian':
        from django.db.models.functions import ExtractYear, ExtractMonth, ExtractDay
        from django.db.models import Max
        
        # 1. Get available years from data
        qs_base = LW321.objects.annotate(
            periode_iso=Concat(
                Substr('periode', 7, 4),  # YYYY
                Value('-'),
                Substr('periode', 4, 2),  # MM
                Value('-'),
                Substr('periode', 1, 2),  # DD
            ),
        ).annotate(
            periode_date=Cast('periode_iso', output_field=DateField())
        ).annotate(
            year=ExtractYear('periode_date'),
            month=ExtractMonth('periode_date'),
            day=ExtractDay('periode_date'),
        )
        
        # Get distinct years
        available_years = list(qs_base.values_list('year', flat=True).distinct().order_by('year'))
        
        # Get distinct months (1-12)
        available_months = [
            {'value': 1, 'name': 'January'},
            {'value': 2, 'name': 'February'},
            {'value': 3, 'name': 'March'},
            {'value': 4, 'name': 'April'},
            {'value': 5, 'name': 'May'},
            {'value': 6, 'name': 'June'},
            {'value': 7, 'name': 'July'},
            {'value': 8, 'name': 'August'},
            {'value': 9, 'name': 'September'},
            {'value': 10, 'name': 'October'},
            {'value': 11, 'name': 'November'},
            {'value': 12, 'name': 'December'},
        ]
        
        # Get filter options
        kanca_list = LW321.objects.values_list('kanca', flat=True).distinct().order_by('kanca')
        
        # 2. Handle Filters
        selected_year = request.GET.get('year', str(available_years[-1]) if available_years else '2025')
        selected_months = request.GET.getlist('month')
        selected_segments = request.GET.getlist('segment')
        selected_kancas = request.GET.getlist('kanca')
        
        # Default: last 3-4 months if none selected
        if not selected_months:
            selected_months = ['8', '9', '10', '11']
        
        if not selected_segments:
            selected_segments = ['ALL']
        if not selected_kancas:
            selected_kancas = ['ALL']
        
        # 3. Build base queryset with annotations
        qs = LW321.objects.all()
        qs = qs.annotate(segment=get_segment_annotation())
        qs = annotate_metrics(qs)
        
        qs = qs.annotate(
            periode_iso=Concat(
                Substr('periode', 7, 4),
                Value('-'),
                Substr('periode', 4, 2),
                Value('-'),
                Substr('periode', 1, 2),
            ),
        ).annotate(
            periode_date=Cast('periode_iso', output_field=DateField())
        ).annotate(
            year=ExtractYear('periode_date'),
            month=ExtractMonth('periode_date'),
            day=ExtractDay('periode_date'),
        )
        
        # Apply year filter
        qs = qs.filter(year=int(selected_year))
        
        # Apply month filter
        selected_months_int = [int(m) for m in selected_months]
        qs = qs.filter(month__in=selected_months_int)
        
        # Apply segment filter
        if 'ALL' not in selected_segments:
            qs = qs.filter(segment__in=selected_segments)
        
        # Apply kanca filter
        if 'ALL' not in selected_kancas:
            qs = qs.filter(kanca__in=selected_kancas)
        
        # 4. Aggregate data: Group by month and day, sum LAR, NPL, SML
        chart_qs = (
            qs.values('month', 'day')
            .annotate(
                total_lar=Sum('lar'),
                total_npl=Sum('npl'),
                total_sml=Sum('sml'),
            )
            .order_by('month', 'day')
        )
        
        # 5. Prepare data structure for chart
        # X-axis: days 1-31
        # Each month is a separate dataset/line
        
        # Month colors (matching the Baki Debit UKER style)
        month_colors = {
            1: {'bg': 'rgba(100, 149, 237, 0.3)', 'border': 'rgba(100, 149, 237, 1)'},    # January - Cornflower Blue
            2: {'bg': 'rgba(255, 99, 132, 0.3)', 'border': 'rgba(255, 99, 132, 1)'},      # February - Pink
            3: {'bg': 'rgba(75, 192, 192, 0.3)', 'border': 'rgba(75, 192, 192, 1)'},      # March - Teal
            4: {'bg': 'rgba(255, 206, 86, 0.3)', 'border': 'rgba(255, 206, 86, 1)'},      # April - Yellow
            5: {'bg': 'rgba(153, 102, 255, 0.3)', 'border': 'rgba(153, 102, 255, 1)'},    # May - Purple
            6: {'bg': 'rgba(255, 159, 64, 0.3)', 'border': 'rgba(255, 159, 64, 1)'},      # June - Orange
            7: {'bg': 'rgba(54, 162, 235, 0.3)', 'border': 'rgba(54, 162, 235, 1)'},      # July - Blue
            8: {'bg': 'rgba(0, 0, 139, 0.3)', 'border': 'rgba(0, 0, 139, 1)'},            # August - Dark Blue
            9: {'bg': 'rgba(255, 165, 0, 0.3)', 'border': 'rgba(255, 165, 0, 1)'},        # September - Orange
            10: {'bg': 'rgba(50, 205, 50, 0.3)', 'border': 'rgba(50, 205, 50, 1)'},       # October - Lime Green
            11: {'bg': 'rgba(30, 144, 255, 0.3)', 'border': 'rgba(30, 144, 255, 1)'},     # November - Dodger Blue
            12: {'bg': 'rgba(220, 20, 60, 0.3)', 'border': 'rgba(220, 20, 60, 1)'},       # December - Crimson
        }
        
        month_names = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }
        
        # Organize data by month for each metric
        data_by_month_lar = {}
        data_by_month_npl = {}
        data_by_month_sml = {}
        
        for row in chart_qs:
            mo = row['month']
            dy = row['day']
            lar_val = float(row['total_lar'] or 0)
            npl_val = float(row['total_npl'] or 0)
            sml_val = float(row['total_sml'] or 0)
            
            if mo not in data_by_month_lar:
                data_by_month_lar[mo] = {}
                data_by_month_npl[mo] = {}
                data_by_month_sml[mo] = {}
            
            data_by_month_lar[mo][dy] = lar_val
            data_by_month_npl[mo][dy] = npl_val
            data_by_month_sml[mo][dy] = sml_val
        
        # Build datasets for each metric
        def build_datasets_for_metric(data_by_month):
            datasets = []
            for mo in sorted(data_by_month.keys()):
                # Create array of 31 days (None for missing days)
                day_data = []
                for d in range(1, 32):
                    day_data.append(data_by_month[mo].get(d, None))
                
                colors = month_colors.get(mo, {'bg': 'rgba(128, 128, 128, 0.3)', 'border': 'rgba(128, 128, 128, 1)'})
                
                datasets.append({
                    'label': month_names.get(mo, f'Month {mo}'),
                    'data': day_data,
                    'backgroundColor': colors['bg'],
                    'borderColor': colors['border'],
                    'borderWidth': 2,
                    'fill': False,  # Line chart without fill
                    'tension': 0.4,  # Smooth curves
                    'pointRadius': 3,
                    'pointHoverRadius': 5,
                })
            return datasets
        
        # X-axis labels: 1-31
        labels = list(range(1, 32))
        
        # Build chart data for each metric
        chart_lar = {
            'labels': labels,
            'datasets': build_datasets_for_metric(data_by_month_lar),
        }
        
        chart_npl = {
            'labels': labels,
            'datasets': build_datasets_for_metric(data_by_month_npl),
        }
        
        chart_sml = {
            'labels': labels,
            'datasets': build_datasets_for_metric(data_by_month_sml),
        }
        
        # 6. Context
        context.update({
            'show_daily_three_charts': True,
            'chart_lar_json': json.dumps(chart_lar, cls=DjangoJSONEncoder),
            'chart_npl_json': json.dumps(chart_npl, cls=DjangoJSONEncoder),
            'chart_sml_json': json.dumps(chart_sml, cls=DjangoJSONEncoder),
            'filters': {
                'years': available_years,
                'months': available_months,
                'segments': ['KUR', 'CC', 'SMALL', 'MEDIUM'],
                'kancas': list(kanca_list),
                'selected_year': selected_year,
                'selected_months': selected_months,
                'selected_segments': selected_segments,
                'selected_kancas': selected_kancas,
            }
        })
    # =================================================================================
    # END SECTION: Timeseries Harian
    # =================================================================================

    # =================================================================================
    # SECTION: OS Small Tables (3 Tables: KONSOL, KANCA ONLY, KCP ONLY)
    # NOTE: Menampilkan data OS Small dengan struktur tabel sesuai format BRI
    #       - Kolom A: Akhir bulan (dipilih) tahun kemarin
    #       - Kolom B: 31 Desember tahun kemarin
    #       - Kolom C: Akhir bulan kemarin
    #       - Kolom D: Tanggal sama bulan kemarin
    #       - Kolom E: Tanggal yang dipilih
    #       - MtD, MoM, YtD, YoY: Perhitungan selisih
    # =================================================================================
    if slug == 'small-os':
        from datetime import date
        from .formulas import (
            get_date_columns, calculate_table_data,
            KANCA_MASTER, UKER_MASTER, KANCA_CODES, KCP_CODES
        )
        
        # 1. Handle date filter
        selected_date_str = request.GET.get('selected_date', '')
        if selected_date_str:
            try:
                selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
            except ValueError:
                selected_date = date.today()
        else:
            selected_date = date.today()
        
        # 2. Get available dates from database
        # Get distinct dates from periode field
        from django.db.models.functions import ExtractYear, ExtractMonth, ExtractDay
        
        qs_base = LW321.objects.annotate(
            periode_iso=Concat(
                Substr('periode', 7, 4),  # YYYY
                Value('-'),
                Substr('periode', 4, 2),  # MM
                Value('-'),
                Substr('periode', 1, 2),  # DD
            ),
        ).annotate(
            periode_date=Cast('periode_iso', output_field=DateField())
        )
        
        available_dates = list(
            qs_base.values_list('periode_date', flat=True)
            .distinct()
            .order_by('-periode_date')[:100]  # Last 100 dates
        )
        
        # 3. Build base queryset with annotations
        qs = LW321.objects.all()
        qs = qs.annotate(segment=get_segment_annotation())
        qs = annotate_metrics(qs)
        
        # 4. Get date columns info
        date_cols = get_date_columns(selected_date)
        
        # 5. Calculate table data for each type
        # Helper function to get kode_kanca from kode_uker
        def get_kode_kanca_from_uker(kode_uker_str):
            """
            Determine the parent KANCA code from a UKER code.
            - If kode_uker is a KANCA itself, return it
            - If kode_uker is a KCP, return its parent KANCA
            """
            try:
                kode_uker = int(kode_uker_str)
            except (ValueError, TypeError):
                return None
            
            # Check if it's a KANCA
            if kode_uker in KANCA_CODES:
                return kode_uker
            
            # Check if it's a KCP, get its parent
            if kode_uker in UKER_MASTER:
                _, kode_kanca_induk = UKER_MASTER[kode_uker]
                return kode_kanca_induk
            
            # Try to find in UKER_MASTER by checking if it appears as key
            for k, (n, induk) in UKER_MASTER.items():
                if k == kode_uker:
                    return induk
            
            return None
        
        # Helper function to get OS by UKER for a specific date
        def get_os_by_uker(target_date, segment_filter='SMALL', uker_filter=None):
            """Get OS aggregated by kode_uker for a specific date"""
            periode_str = target_date.strftime("%d/%m/%Y")
            
            qs_filtered = qs.filter(periode=periode_str, segment=segment_filter)
            
            if uker_filter == 'KANCA':
                kanca_codes_str = [str(c) for c in KANCA_CODES]
                qs_filtered = qs_filtered.filter(kode_uker__in=kanca_codes_str)
            elif uker_filter == 'KCP':
                kcp_codes_str = [str(c) for c in KCP_CODES]
                qs_filtered = qs_filtered.filter(kode_uker__in=kcp_codes_str)
            
            result = {}
            for row in qs_filtered.values('kode_uker').annotate(total_os=Sum('os')):
                result[row['kode_uker']] = float(row['total_os'] or 0)
            return result
        
        # Helper function to get OS grouped by KANCA (for KONSOL table)
        def get_os_by_kanca(target_date, segment_filter='SMALL'):
            """
            Get OS aggregated by kode_kanca for KONSOL table.
            This groups all UKER (both KANCA and KCP) under their parent KANCA.
            """
            periode_str = target_date.strftime("%d/%m/%Y")
            
            qs_filtered = qs.filter(periode=periode_str, segment=segment_filter)
            
            # Get all OS by kode_uker first
            os_by_uker = {}
            for row in qs_filtered.values('kode_uker').annotate(total_os=Sum('os')):
                os_by_uker[row['kode_uker']] = float(row['total_os'] or 0)
            
            # Now group by KANCA
            os_by_kanca = {}
            for kode_uker_str, os_value in os_by_uker.items():
                kode_kanca = get_kode_kanca_from_uker(kode_uker_str)
                if kode_kanca:
                    if kode_kanca not in os_by_kanca:
                        os_by_kanca[kode_kanca] = 0
                    os_by_kanca[kode_kanca] += os_value
            
            return os_by_kanca
        
        # 6. Build KONSOL table (grouped by KANCA)
        def build_konsol_table():
            rows = []
            totals = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}
            
            # Get OS for each date, grouped by KANCA
            os_a = get_os_by_kanca(date_cols['A']['date'])
            os_b = get_os_by_kanca(date_cols['B']['date'])
            os_c = get_os_by_kanca(date_cols['C']['date'])
            os_d = get_os_by_kanca(date_cols['D']['date'])
            os_e = get_os_by_kanca(date_cols['E']['date'])
            
            row_num = 1
            for kode_kanca in sorted(KANCA_CODES):
                nama_kanca = KANCA_MASTER.get(kode_kanca, f"KANCA {kode_kanca}")
                
                # Get OS values for this KANCA (already summed with its KCPs)
                val_a = os_a.get(kode_kanca, 0)
                val_b = os_b.get(kode_kanca, 0)
                val_c = os_c.get(kode_kanca, 0)
                val_d = os_d.get(kode_kanca, 0)
                val_e = os_e.get(kode_kanca, 0)
                
                row = {
                    'no': row_num,
                    'kode_kanca': kode_kanca,
                    'kanca': nama_kanca,
                    'A': val_a,
                    'B': val_b,
                    'C': val_c,
                    'D': val_d,
                    'E': val_e,
                    'DtD': val_e - val_d,
                    'DtD_pct': ((val_e - val_d) / val_d * 100) if val_d else 0,
                    'MoM': val_e - val_b,
                    'MoM_pct': ((val_e - val_b) / val_b * 100) if val_b else 0,
                    'MtD': val_e - val_c,
                    'MtD_pct': ((val_e - val_c) / val_c * 100) if val_c else 0,
                    'YtD': val_e - val_a,
                    'YtD_pct': ((val_e - val_a) / val_a * 100) if val_a else 0,
                }
                
                rows.append(row)
                totals['A'] += val_a
                totals['B'] += val_b
                totals['C'] += val_c
                totals['D'] += val_d
                totals['E'] += val_e
                row_num += 1
            
            # Calculate totals derived values
            totals['DtD'] = totals['E'] - totals['D']
            totals['DtD_pct'] = (totals['DtD'] / totals['D'] * 100) if totals['D'] else 0
            totals['MoM'] = totals['E'] - totals['B']
            totals['MoM_pct'] = (totals['MoM'] / totals['B'] * 100) if totals['B'] else 0
            totals['MtD'] = totals['E'] - totals['C']
            totals['MtD_pct'] = (totals['MtD'] / totals['C'] * 100) if totals['C'] else 0
            totals['YtD'] = totals['E'] - totals['A']
            totals['YtD_pct'] = (totals['YtD'] / totals['A'] * 100) if totals['A'] else 0
            
            return rows, totals
        
        # 7. Build KANCA ONLY table
        def build_kanca_only_table():
            rows = []
            totals = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}
            
            os_a = get_os_by_uker(date_cols['A']['date'], uker_filter='KANCA')
            os_b = get_os_by_uker(date_cols['B']['date'], uker_filter='KANCA')
            os_c = get_os_by_uker(date_cols['C']['date'], uker_filter='KANCA')
            os_d = get_os_by_uker(date_cols['D']['date'], uker_filter='KANCA')
            os_e = get_os_by_uker(date_cols['E']['date'], uker_filter='KANCA')
            
            row_num = 1
            for kode_kanca in sorted(KANCA_CODES):
                nama_kanca = KANCA_MASTER.get(kode_kanca, f"KANCA {kode_kanca}")
                kode_str = str(kode_kanca)
                
                val_a = os_a.get(kode_str, 0)
                val_b = os_b.get(kode_str, 0)
                val_c = os_c.get(kode_str, 0)
                val_d = os_d.get(kode_str, 0)
                val_e = os_e.get(kode_str, 0)
                
                row = {
                    'no': row_num,
                    'kode_uker': kode_kanca,
                    'uker': nama_kanca,
                    'kode_kanca': kode_kanca,
                    'kanca': nama_kanca,
                    'A': val_a,
                    'B': val_b,
                    'C': val_c,
                    'D': val_d,
                    'E': val_e,
                    'DtD': val_e - val_d,
                    'DtD_pct': ((val_e - val_d) / val_d * 100) if val_d else 0,
                    'MoM': val_e - val_b,
                    'MoM_pct': ((val_e - val_b) / val_b * 100) if val_b else 0,
                    'MtD': val_e - val_c,
                    'MtD_pct': ((val_e - val_c) / val_c * 100) if val_c else 0,
                    'YtD': val_e - val_a,
                    'YtD_pct': ((val_e - val_a) / val_a * 100) if val_a else 0,
                    'komitmen': 0, 'komitmen_pct_ach': 0, 'komitmen_gab_real': 0,
                    'komitmen_vs_c': 0, 'komitmen_vs_c_pct': 0,
                    'komitmen_vs_b': 0, 'komitmen_vs_b_pct': 0,
                    'rkap': 0, 'rkap_gab_real': 0, 'rkap_vs_komitmen': 0, 'rkap_pct_ach': 0,
                }
                
                rows.append(row)
                totals['A'] += val_a
                totals['B'] += val_b
                totals['C'] += val_c
                totals['D'] += val_d
                totals['E'] += val_e
                row_num += 1
            
            totals['DtD'] = totals['E'] - totals['D']
            totals['DtD_pct'] = (totals['DtD'] / totals['D'] * 100) if totals['D'] else 0
            totals['MoM'] = totals['E'] - totals['B']
            totals['MoM_pct'] = (totals['MoM'] / totals['B'] * 100) if totals['B'] else 0
            totals['MtD'] = totals['E'] - totals['C']
            totals['MtD_pct'] = (totals['MtD'] / totals['C'] * 100) if totals['C'] else 0
            totals['YtD'] = totals['E'] - totals['A']
            totals['YtD_pct'] = (totals['YtD'] / totals['A'] * 100) if totals['A'] else 0
            
            return rows, totals
        
        # 8. Build KCP ONLY table
        def build_kcp_only_table():
            rows = []
            totals = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}
            
            os_a = get_os_by_uker(date_cols['A']['date'], uker_filter='KCP')
            os_b = get_os_by_uker(date_cols['B']['date'], uker_filter='KCP')
            os_c = get_os_by_uker(date_cols['C']['date'], uker_filter='KCP')
            os_d = get_os_by_uker(date_cols['D']['date'], uker_filter='KCP')
            os_e = get_os_by_uker(date_cols['E']['date'], uker_filter='KCP')
            
            # Build list with kode_kanca for sorting
            kcp_list = []
            for kode_kcp in KCP_CODES:
                if kode_kcp in UKER_MASTER:
                    nama_kcp, kode_kanca_induk = UKER_MASTER[kode_kcp]
                    nama_kanca = KANCA_MASTER.get(kode_kanca_induk, '')
                else:
                    nama_kcp = f"KCP {kode_kcp}"
                    nama_kanca = ''
                    kode_kanca_induk = 0
                
                kcp_list.append((kode_kanca_induk, kode_kcp, nama_kcp, nama_kanca))
            
            # Sort by kode_kanca ascending, then by kode_kcp
            kcp_list.sort(key=lambda x: (x[0], x[1]))
            
            row_num = 1
            for kode_kanca_induk, kode_kcp, nama_kcp, nama_kanca in kcp_list:
                kode_str = str(kode_kcp)
                
                val_a = os_a.get(kode_str, 0)
                val_b = os_b.get(kode_str, 0)
                val_c = os_c.get(kode_str, 0)
                val_d = os_d.get(kode_str, 0)
                val_e = os_e.get(kode_str, 0)
                
                row = {
                    'no': row_num,
                    'kode_uker': kode_kcp,
                    'uker': nama_kcp,
                    'kode_kanca': kode_kanca_induk,
                    'kanca': nama_kanca,
                    'A': val_a,
                    'B': val_b,
                    'C': val_c,
                    'D': val_d,
                    'E': val_e,
                    'DtD': val_e - val_d,
                    'DtD_pct': ((val_e - val_d) / val_d * 100) if val_d else 0,
                    'MoM': val_e - val_b,
                    'MoM_pct': ((val_e - val_b) / val_b * 100) if val_b else 0,
                    'MtD': val_e - val_c,
                    'MtD_pct': ((val_e - val_c) / val_c * 100) if val_c else 0,
                    'YtD': val_e - val_a,
                    'YtD_pct': ((val_e - val_a) / val_a * 100) if val_a else 0,
                    'komitmen': 0, 'komitmen_pct_ach': 0, 'komitmen_gab_real': 0,
                    'komitmen_vs_c': 0, 'komitmen_vs_c_pct': 0,
                    'komitmen_vs_b': 0, 'komitmen_vs_b_pct': 0,
                    'rkap': 0, 'rkap_gab_real': 0, 'rkap_vs_komitmen': 0, 'rkap_pct_ach': 0,
                }
                
                rows.append(row)
                totals['A'] += val_a
                totals['B'] += val_b
                totals['C'] += val_c
                totals['D'] += val_d
                totals['E'] += val_e
                row_num += 1
            
            totals['DtD'] = totals['E'] - totals['D']
            totals['DtD_pct'] = (totals['DtD'] / totals['D'] * 100) if totals['D'] else 0
            totals['MoM'] = totals['E'] - totals['B']
            totals['MoM_pct'] = (totals['MoM'] / totals['B'] * 100) if totals['B'] else 0
            totals['MtD'] = totals['E'] - totals['C']
            totals['MtD_pct'] = (totals['MtD'] / totals['C'] * 100) if totals['C'] else 0
            totals['YtD'] = totals['E'] - totals['A']
            totals['YtD_pct'] = (totals['YtD'] / totals['A'] * 100) if totals['A'] else 0
            
            return rows, totals
        
        # Build all tables
        konsol_rows, konsol_totals = build_konsol_table()
        kanca_rows, kanca_totals = build_kanca_only_table()
        kcp_rows, kcp_totals = build_kcp_only_table()
        
        # Header info for calculations
        dtd_header = f"{date_cols['E']['label']} - {date_cols['D']['label']}"
        mom_header = f"{date_cols['E']['label']} - {date_cols['B']['label']}"
        mtd_header = f"{date_cols['E']['label']} - {date_cols['C']['label']}"
        ytd_header = f"{date_cols['E']['label']} - {date_cols['A']['label']}"
        
        # Context
        context.update({
            'show_os_tables': True,
            'selected_date': selected_date,
            'selected_date_str': selected_date.strftime('%Y-%m-%d'),
            'available_dates': available_dates,
            'date_columns': date_cols,
            'dtd_header': dtd_header,
            'mom_header': mom_header,
            'mtd_header': mtd_header,
            'ytd_header': ytd_header,
            'tables': {
                'konsol': {
                    'title': 'TOTAL OS SMALL KANCA KONSOL',
                    'rows': konsol_rows,
                    'totals': konsol_totals,
                },
                'kanca': {
                    'title': 'TOTAL OS SMALL KANCA ONLY',
                    'rows': kanca_rows,
                    'totals': kanca_totals,
                },
                'kcp': {
                    'title': 'TOTAL OS SMALL KCP ONLY',
                    'rows': kcp_rows,
                    'totals': kcp_totals,
                },
            },
        })
    # =================================================================================
    # END SECTION: OS Small Tables
    # =================================================================================
    
    # =================================================================================
    # SECTION: DPK Small Tables - NEW with kol_adk filter
    #       - Filtered by kol_adk='2' (Kolektibilitas DPK)
    #       - Uses refactored modular metric handler
    # =================================================================================
    elif slug == 'small-dpk':
        from .formulas.metric_handlers import handle_dpk_view
        
        # Use modular handler - DPK filtered by kol_adk='2'
        context.update(handle_dpk_view(request, segment_filter='SMALL'))
    # =================================================================================
    # END SECTION: DPK Small Tables
    # =================================================================================

    # =================================================================================
    # SECTION: %DPK Small Tables
    #       - %DPK = (DPK / OS) * 100
    #       - Uses refactored modular metric handler
    # =================================================================================
    elif slug == 'small-dpk-pct':
        from .formulas.metric_handlers import handle_dpk_pct_view
        
        # Use modular handler - %DPK calculated as (DPK/OS)*100
        context.update(handle_dpk_pct_view(request, segment_filter='SMALL'))
    # =================================================================================
    # END SECTION: %DPK Small Tables
    # =================================================================================

    # =================================================================================
    # SECTION: NPL Small Tables
    #       - NPL = KL + D + M (from calculations.py)
    #       - Uses refactored modular metric handler
    # =================================================================================
    elif slug == 'small-npl':
        from .formulas.metric_handlers import handle_npl_view
        
        # Use modular handler - NPL calculated from calculations.py
        context.update(handle_npl_view(request, segment_filter='SMALL'))
    # =================================================================================
    # END SECTION: NPL Small Tables
    # =================================================================================

    # =================================================================================
    # SECTION: %NPL Small Tables
    #       - %NPL = (NPL / OS) * 100
    #       - Uses refactored modular metric handler
    # =================================================================================
    elif slug == 'small-npl-pct':
        from .formulas.metric_handlers import handle_npl_pct_view
        
        # Use modular handler - %NPL calculated as (NPL/OS)*100
        context.update(handle_npl_pct_view(request, segment_filter='SMALL'))
    # =================================================================================
    # END SECTION: %NPL Small Tables
    # =================================================================================

    # =================================================================================
    # SECTION: LR Small Tables
    #       - LR = Lancar if (kol_adk == '1' AND flag_restruk == 'Y')
    #       - Uses refactored modular metric handler
    # =================================================================================
    elif slug == 'small-lr':
        from .formulas.metric_handlers import handle_lr_view
        
        # Use modular handler - LR calculated from calculations.py
        context.update(handle_lr_view(request, segment_filter='SMALL'))
    # =================================================================================
    # END SECTION: LR Small Tables
    # =================================================================================

    # =================================================================================
    # SECTION: LAR Small Tables
    #       - LAR = SML + NPL + LR
    #       - Uses refactored modular metric handler
    # =================================================================================
    elif slug == 'small-lar':
        from .formulas.metric_handlers import handle_lar_view
        
        # Use modular handler - LAR calculated from calculations.py
        context.update(handle_lar_view(request, segment_filter='SMALL'))
    # =================================================================================
    # END SECTION: LAR Small Tables
    # =================================================================================

    # =================================================================================
    # SECTION: NSB Small Tables
    #       - NSB = COUNT(DISTINCT cifno) for segment SMALL
    #       - Counts unique customers (nasabah)
    #       - Uses refactored modular metric handler
    # =================================================================================
    elif slug == 'small-nsb':
        from .formulas.metric_handlers import handle_nsb_view
        
        # Use modular handler - NSB counts distinct CIFNO
        context.update(handle_nsb_view(request, segment_filter='SMALL'))
    # =================================================================================
    # END SECTION: NSB Small Tables
    # =================================================================================


    return render(request, 'dashboard/metric_page.html', context)
