"""
Template/Example untuk implementasi pengolahan data dashboard
File ini berisi contoh-contoh yang perlu disesuaikan dengan kebutuhan real

NOTE: File ini adalah TEMPLATE, sesuaikan dengan struktur data 38 kolom Anda
"""

import pandas as pd
from decimal import Decimal, InvalidOperation
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Avg, Q, F, Case, When, IntegerField
from django.db.models.functions import TruncDate, TruncMonth, ExtractWeekDay
from dashboard.models import LoanData, ProcessedData
from dashboard.utils import (
    get_date_range, calculate_growth_rate, format_currency,
    format_number, chunk_queryset
)


# ============================================================================
# CONTOH 1: Dashboard OS (Outstanding)
# ============================================================================

def get_dashboard_os_data(date_from=None, date_to=None):
    """
    Contoh pengolahan data untuk Dashboard OS
    
    Returns:
        dict: Data untuk dashboard OS
    """
    
    # Set default date range jika tidak ada
    if not date_from or not date_to:
        date_from, date_to = get_date_range('this_month')
    
    # Query data pinjaman
    loans = LoanData.objects.filter(
        tgl_realisasi__range=[date_from, date_to]
    )

    # Hitung total outstanding (plafon)
    total_os = loans.aggregate(
        total=Sum('plafon')
    )['total'] or 0

    # Hitung jumlah CIF unik
    total_customers = loans.values('cif_no').distinct().count()

    # OS by kanca
    os_by_branch = loans.values('kanca').annotate(
        total=Sum('plafon'),
        count=Count('id')
    ).order_by('-total')

    # OS by LN type
    os_by_product = loans.values('ln_type').annotate(
        total=Sum('plafon'),
        count=Count('id')
    ).order_by('-total')

    # OS trend (daily untuk chart)
    os_trend = loans.annotate(
        date=TruncDate('tgl_realisasi')
    ).values('date').annotate(
        daily_os=Sum('plafon')
    ).order_by('date')

    # Calculate growth rate (compare dengan periode sebelumnya)
    last_month_from = date_from - timedelta(days=30)
    last_month_to = date_to - timedelta(days=30)

    last_month_os = LoanData.objects.filter(
        tgl_realisasi__range=[last_month_from, last_month_to]
    ).aggregate(total=Sum('plafon'))['total'] or 0
    
    growth = calculate_growth_rate(total_os, last_month_os)
    
    return {
        'total_os': total_os,
        'total_os_formatted': format_currency(total_os),
        'total_customers': total_customers,
        'total_customers_formatted': format_number(total_customers),
        'os_by_branch': list(os_by_branch),
        'os_by_product': list(os_by_product),
        'os_trend': list(os_trend),
        'growth_rate': growth,
        'date_range': {
            'from': date_from,
            'to': date_to
        }
    }


# ============================================================================
# CONTOH 2: Dashboard Summary
# ============================================================================

def get_dashboard_summary_data(sub_type='medium_only', date_from=None, date_to=None):
    """
    Contoh pengolahan data untuk Dashboard Summary
    
    Args:
        sub_type: 'medium_only', 'konsol', atau 'only'
    
    Returns:
        dict: Data untuk dashboard summary
    """
    
    if not date_from or not date_to:
        date_from, date_to = get_date_range('this_month')
    
    # Base query
    base_query = LoanData.objects.filter(
        tgl_realisasi__range=[date_from, date_to]
    )
    
    # Filter berdasarkan sub_type (sesuaikan dengan aturan bisnis Anda)
    if sub_type == 'medium_only':
        # Contoh: pinjaman dengan plafon tertentu
        filtered_query = base_query.filter(
            plafon__gte=50000000,  # >= 50 juta
            plafon__lt=500000000   # < 500 juta
        )
    elif sub_type == 'konsol':
        # Contoh: pinjaman yang sudah restrukturisasi
        filtered_query = base_query.filter(
            flag_restruk='Ya'
        )
    elif sub_type == 'only':
        filtered_query = base_query
    else:
        filtered_query = base_query
    
    # Summary statistics
    summary_stats = filtered_query.aggregate(
        total_loans=Count('id'),
        total_plafon=Sum('plafon'),
        avg_plafon=Avg('plafon'),
        total_customers=Count('cif_no', distinct=True)
    )
    
    # Kolektibilitas summary (jumlah account per kategori)
    kolektibilitas_summary = filtered_query.aggregate(
        lancar=Sum(Case(When(kolektibilitas_lancar='1', then=1), default=0, output_field=IntegerField())),
        dpk=Sum(Case(When(kolektibilitas_dpk='1', then=1), default=0, output_field=IntegerField())),
        kurang_lancar=Sum(Case(When(kolektibilitas_kurang_lancar='1', then=1), default=0, output_field=IntegerField())),
        diragukan=Sum(Case(When(kolektibilitas_diragukan='1', then=1), default=0, output_field=IntegerField())),
        macet=Sum(Case(When(kolektibilitas_macet='1', then=1), default=0, output_field=IntegerField())),
    )
    
    # By kanca
    by_kanca = filtered_query.values('kanca').annotate(
        count=Count('id'),
        total_plafon=Sum('plafon')
    ).order_by('-total_plafon')
    
    # By jangka waktu
    by_tenor = filtered_query.values('jangka_waktu').annotate(
        count=Count('id'),
        total_plafon=Sum('plafon')
    ).order_by('jangka_waktu')
    
    # Top debitur (by plafon)
    top_customers = filtered_query.values('cif_no', 'nama_debitur').annotate(
        total_plafon=Sum('plafon'),
        loan_count=Count('id')
    ).order_by('-total_plafon')[:10]
    
    return {
        'sub_type': sub_type,
        'summary_stats': summary_stats,
        'kolektibilitas_summary': kolektibilitas_summary,
        'by_kanca': list(by_kanca),
        'by_tenor': list(by_tenor),
        'top_customers': list(top_customers),
        'date_range': {
            'from': date_from,
            'to': date_to
        }
    }


# ============================================================================
# CONTOH 3: Dashboard Grafik Harian
# ============================================================================

def get_dashboard_grafik_harian_data(date_from=None, date_to=None):
    """
    Contoh pengolahan data untuk Dashboard Grafik Harian
    
    Returns:
        dict: Data untuk grafik harian
    """
    
    if not date_from or not date_to:
        date_from, date_to = get_date_range('last_30_days')
    
    # Daily loan data
    daily_data = LoanData.objects.filter(
        tgl_realisasi__range=[date_from, date_to]
    ).annotate(
        date=TruncDate('tgl_realisasi')
    ).values('date').annotate(
        total_loans=Count('id'),
        total_plafon=Sum('plafon'),
        avg_plafon=Avg('plafon')
    ).order_by('date')
    
    # Prepare chart data
    dates = []
    loan_counts = []
    amounts = []
    
    for data in daily_data:
        dates.append(data['date'].strftime('%Y-%m-%d'))
        loan_counts.append(data['total_loans'])
        amounts.append(float(data['total_plafon'] or 0))
    
    # Calculate daily average
    total_days = (date_to - date_from).days + 1
    avg_daily_loans = sum(loan_counts) / total_days if total_days > 0 else 0
    avg_daily_amount = sum(amounts) / total_days if total_days > 0 else 0
    
    # Day of week analysis
    loans_with_weekday = LoanData.objects.filter(
        tgl_realisasi__range=[date_from, date_to]
    ).annotate(
        weekday=ExtractWeekDay('tgl_realisasi')
    ).values('weekday').annotate(
        count=Count('id'),
        total_plafon=Sum('plafon')
    ).order_by('weekday')
    
    weekday_map = {
        1: 'Minggu',
        2: 'Senin',
        3: 'Selasa',
        4: 'Rabu',
        5: 'Kamis',
        6: 'Jumat',
        7: 'Sabtu'
    }
    
    return {
        'dates': dates,
        'loan_counts': loan_counts,
        'amounts': amounts,
        'avg_daily_loans': round(avg_daily_loans, 2),
        'avg_daily_amount': avg_daily_amount,
        'avg_daily_amount_formatted': format_currency(avg_daily_amount),
        'weekday_analysis': [
            {
                'day': weekday_map.get(int(item['weekday']), 'Tidak diketahui'),
                'count': item['count'],
                'amount': item['total_plafon']
            }
            for item in loans_with_weekday
        ],
        'date_range': {
            'from': date_from,
            'to': date_to
        }
    }


# ============================================================================
# CONTOH 4: Proses Upload Data
# ============================================================================

def process_loan_data_row(row):
    """
    Contoh fungsi untuk memproses satu baris data
    
    Args:
        row: Pandas Series (satu baris dari DataFrame)
    
    Returns:
        dict: {'success': True/False, 'error': '...', 'data': LoanData object}
    """
    
    try:
        # Normalisasi kolom: terima baik nama kolom asli maupun nama model
        def take(field_name, fallback_field=None):
            if field_name in row:
                return row[field_name]
            if fallback_field and fallback_field in row:
                return row[fallback_field]
            return None

        # Parser sederhana
        def parse_string(value):
            if pd.isna(value) or value is None:
                return ''
            return str(value).strip()

        def parse_decimal(value):
            if pd.isna(value) or value in (None, ''):
                return None
            try:
                if isinstance(value, str):
                    value = value.replace(',', '').strip()
                    if not value:
                        return None
                return Decimal(value)
            except (InvalidOperation, ValueError, TypeError):
                return None

        def parse_int(value):
            if pd.isna(value) or value in (None, ''):
                return None
            try:
                return int(float(value))
            except (ValueError, TypeError):
                return None

        def parse_date(value):
            if pd.isna(value) or value in (None, ''):
                return None
            parsed = pd.to_datetime(value, errors='coerce')
            if pd.isna(parsed):
                return None
            return parsed.date()

        # Validasi data wajib (gunakan nama model)
        required_fields = ['periode', 'nomor_rekening', 'cif_no', 'plafon']
        for field in required_fields:
            value = take(field, field.upper())
            if pd.isna(value) or str(value).strip() == '':
                return {
                    'success': False,
                    'error': f'Field {field} wajib diisi'
                }
        nomor_rekening = parse_string(take('nomor_rekening', 'NOMOR_REKENING'))

        defaults = {
            'periode': parse_string(take('periode', 'PERIODE')),
            'kanca': parse_string(take('kanca', 'KANCA')),
            'kode_uker': parse_string(take('kode_uker', 'KODE_UKER')),
            'uker': parse_string(take('uker', 'UKER')),
            'ln_type': parse_string(take('ln_type', 'LN_TYPE')),
            'nama_debitur': parse_string(take('nama_debitur', 'NAMA_DEBITUR')),
            'plafon': parse_decimal(take('plafon', 'PLAFON')),
            'next_pmt_date': parse_date(take('next_pmt_date', 'NEXT_PMT_DATE')),
            'next_int_pmt_date': parse_date(take('next_int_pmt_date', 'NEXT_INT_PMT_DATE')),
            'rate': parse_decimal(take('rate', 'RATE')),
            'tgl_menunggak': parse_date(take('tgl_menunggak', 'TGL_MENUNGGAK')),
            'tgl_realisasi': parse_date(take('tgl_realisasi', 'TGL_REALISASI')),
            'tgl_jatuh_tempo': parse_date(take('tgl_jatuh_tempo', 'TGL JATUH TEMPO')),
            'jangka_waktu': parse_int(take('jangka_waktu', 'JANGKA WAKTU')),
            'flag_restruk': parse_string(take('flag_restruk', 'FLAG RESTRUK')),
            'cif_no': parse_string(take('cif_no', 'CIFNO')),
            'kolektibilitas_lancar': parse_string(take('kolektibilitas_lancar', 'KOLEKTIBILITAS LANCAR')),
            'kolektibilitas_dpk': parse_string(take('kolektibilitas_dpk', 'KOLEKTIBILITAS DPK')),
            'kolektibilitas_kurang_lancar': parse_string(take('kolektibilitas_kurang_lancar', 'KOLEKTIBILITAS KURANG LANCAR')),
            'kolektibilitas_diragukan': parse_string(take('kolektibilitas_diragukan', 'KOLEKTIBILITAS DIRAGUKAN')),
            'kolektibilitas_macet': parse_string(take('kolektibilitas_macet', 'KOLEKTIBILITAS MACET')),
            'tunggakan_pokok': parse_decimal(take('tunggakan_pokok', 'TUNGGAKAN POKOK')),
            'tunggakan_bunga': parse_decimal(take('tunggakan_bunga', 'TUNGGAKAN BUNGA')),
            'tunggakan_pinalti': parse_decimal(take('tunggakan_pinalti', 'TUNGGAKAN PINALTI')),
            'code': parse_string(take('code', 'CODE')),
            'description': parse_string(take('description', 'DESCRIPTION')),
            'kol_adk': parse_string(take('kol_adk', 'KOL_ADK')),
            'pn_pengelola_singlepn': parse_string(take('pn_pengelola_singlepn', 'PN PENGELOLA SINGLEPN')),
            'pn_pengelola_1': parse_string(take('pn_pengelola_1', 'PN PENGELOLA 1')),
            'pn_pemrakarsa': parse_string(take('pn_pemrakarsa', 'PN PEMRAKARSA')),
            'pn_referral': parse_string(take('pn_referral', 'PN REFERRAL')),
            'pn_restruk': parse_string(take('pn_restruk', 'PN RESTRUK')),
            'pn_pengelola_2': parse_string(take('pn_pengelola_2', 'PN PENGELOLA 2')),
            'pn_pemutus': parse_string(take('pn_pemutus', 'PN PEMUTUS')),
            'pn_crm': parse_string(take('pn_crm', 'PN CRM')),
            'pn_rm_referral_naik_segmentasi': parse_string(take('pn_rm_referral_naik_segmentasi', 'PN RM REFERRAL NAIK SEGMENTASI')),
            'pn_rm_crr': parse_string(take('pn_rm_crr', 'PN RM CRR')),
        }

        loan_data, created = LoanData.objects.update_or_create(
            nomor_rekening=nomor_rekening,
            defaults=defaults
        )

        return {
            'success': True,
            'error': '',
            'data': loan_data,
            'created': created
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# ============================================================================
# CONTOH 5: Batch Processing untuk Data Besar
# ============================================================================

def process_large_dataset_batch(queryset, batch_size=1000):
    """
    Contoh processing data dalam batch untuk performa optimal
    
    Args:
        queryset: Django QuerySet
        batch_size: Ukuran batch
    
    Returns:
        dict: Hasil processing
    """
    
    from dashboard.utils import chunk_queryset
    
    total_processed = 0
    total_success = 0
    total_failed = 0
    errors = []
    
    # Process in chunks
    for chunk in chunk_queryset(queryset, batch_size):
        for item in chunk:
            try:
                # Processing logic here
                # Contoh: update status, calculate metrics, etc.
                
                total_success += 1
            except Exception as e:
                total_failed += 1
                errors.append({
                    'item_id': item.id,
                    'error': str(e)
                })
            
            total_processed += 1
    
    return {
        'total_processed': total_processed,
        'total_success': total_success,
        'total_failed': total_failed,
        'errors': errors[:100]  # Limit error log
    }


# ============================================================================
# CONTOH 6: Export Data
# ============================================================================

def export_dashboard_data(dashboard_type, date_from, date_to, format='excel'):
    """
    Contoh export data dashboard ke Excel/CSV
    
    Args:
        dashboard_type: 'os', 'summary', 'grafik_harian'
        date_from: Start date
        date_to: End date
        format: 'excel' or 'csv'
    
    Returns:
        File response
    """
    
    import pandas as pd
    from django.http import HttpResponse
    from io import BytesIO
    
    # Get data berdasarkan tipe dashboard
    if dashboard_type == 'os':
        data = get_dashboard_os_data(date_from, date_to)
        df = pd.DataFrame(data['os_by_branch'])
    elif dashboard_type == 'summary':
        data = get_dashboard_summary_data('medium_only', date_from, date_to)
        df = pd.DataFrame(data['by_kanca'])
    else:
        data = get_dashboard_grafik_harian_data(date_from, date_to)
        df = pd.DataFrame({
            'Tanggal': data['dates'],
            'Jumlah Pinjaman': data['loan_counts'],
            'Total Plafon': data['amounts']
        })
    
    # Export
    if format == 'excel':
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
        
        output.seek(0)
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="dashboard_{dashboard_type}_{date_from}_{date_to}.xlsx"'
        
    else:  # CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="dashboard_{dashboard_type}_{date_from}_{date_to}.csv"'
        df.to_csv(path_or_buf=response, index=False)
    
    return response


# ============================================================================
# TEMPLATE: Sesuaikan dengan Struktur 38 Kolom Anda
# ============================================================================

"""
DAFTAR KOLOM LOANDATA (38 KOLOM) - SESUAIKAN DENGAN SUMBER DATA ANDA
====================================================================

1.  periode
2.  kanca
3.  kode_uker
4.  uker
5.  ln_type
6.  nomor_rekening
7.  nama_debitur
8.  plafon
9.  next_pmt_date
10. next_int_pmt_date
11. rate
12. tgl_menunggak
13. tgl_realisasi
14. tgl_jatuh_tempo
15. jangka_waktu
16. flag_restruk
17. cif_no
18. kolektibilitas_lancar
19. kolektibilitas_dpk
20. kolektibilitas_kurang_lancar
21. kolektibilitas_diragukan
22. kolektibilitas_macet
23. tunggakan_pokok
24. tunggakan_bunga
25. tunggakan_pinalti
26. code
27. description
28. kol_adk
29. pn_pengelola_singlepn
30. pn_pengelola_1
31. pn_pemrakarsa
32. pn_referral
33. pn_restruk
34. pn_pengelola_2
35. pn_pemutus
36. pn_crm
37. pn_rm_referral_naik_segmentasi
38. pn_rm_crr

Pastikan pipeline upload, proses agregasi, dokumentasi, dan visualisasi Anda
menggunakan nama field di atas agar konsisten dengan model `LoanData`.
"""
