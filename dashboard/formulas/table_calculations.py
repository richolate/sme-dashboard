"""
Table Calculations for Dashboard Tables
Menghitung data untuk tabel seperti OS Small, OS Medium, dll.

Struktur Kolom:
- Kolom A: 31 Desember tahun kemarin (label: bulan-tahun saja, contoh: Dec-2024)
- Kolom B: Tanggal yang sama tapi bulan kemarin
- Kolom C: Tanggal akhir bulan kemarin
- Kolom D: H-1 (kemarin)
- Kolom E: Hari ini (yang dipilih user)

Perhitungan:
- DtD (Day to Day): E - D
- MoM (Month on Month): E - B
- MtD (Month to Date): E - C
- YtD (Year to Date): E - A
"""

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from calendar import monthrange
from typing import Dict, List, Tuple, Optional, Any
from decimal import Decimal
from django.db.models import Sum, Q
from django.db.models.functions import Cast, Concat, Substr, ExtractYear, ExtractMonth, ExtractDay
from django.db.models import DateField, Value


def get_date_columns(selected_date: date) -> Dict[str, Dict[str, Any]]:
    """
    Menghitung tanggal-tanggal referensi berdasarkan tanggal yang dipilih.
    
    Args:
        selected_date: Tanggal yang dipilih user (misal: 2025-10-09)
    
    Returns:
        Dictionary berisi tanggal dan label untuk setiap kolom
    """
    # Selected date info
    year = selected_date.year
    month = selected_date.month
    day = selected_date.day
    
    # Kolom E: Hari ini (tanggal yang dipilih)
    col_e = selected_date
    
    # Kolom A: 31 Desember tahun kemarin (fixed bulan Desember)
    # Contoh: jika dipilih tanggal di tahun 2025, maka A = 31-Dec-2024
    col_a = date(year - 1, 12, 31)
    
    # Kolom B: Tanggal yang sama tapi bulan kemarin
    # Contoh: jika dipilih 09-Oct-2025, maka B = 09-Sep-2025
    col_b = selected_date - relativedelta(months=1)
    
    # Kolom C: Tanggal akhir bulan kemarin
    # Contoh: jika dipilih 09-Oct-2025, maka C = 30-Sep-2025
    first_day_this_month = date(year, month, 1)
    last_day_prev_month = first_day_this_month - timedelta(days=1)
    col_c = last_day_prev_month
    
    # Kolom D: H-1 (kemarin)
    # Contoh: jika dipilih 09-Oct-2025, maka D = 08-Oct-2025
    col_d = selected_date - timedelta(days=1)
    
    # Format labels
    def format_date_label(d: date) -> str:
        return d.strftime("%d-%b-%y")  # Format: 09-Oct-25
    
    return {
        'A': {
            'date': col_a,
            'label': f"{col_a.strftime('%b')}-{col_a.year}",  # Format: Dec-2024
            'description': f"31 Desember {col_a.year}",
        },
        'B': {
            'date': col_b,
            'label': format_date_label(col_b),
            'description': f"{col_b.day} {col_b.strftime('%B')} {col_b.year}",
        },
        'C': {
            'date': col_c,
            'label': format_date_label(col_c),
            'description': f"Akhir {col_c.strftime('%B')} {col_c.year}",
        },
        'D': {
            'date': col_d,
            'label': format_date_label(col_d),
            'description': f"H-1 ({col_d.day} {col_d.strftime('%B')} {col_d.year})",
        },
        'E': {
            'date': col_e,
            'label': format_date_label(col_e),
            'description': f"Hari ini ({col_e.day} {col_e.strftime('%B')} {col_e.year})",
        },
    }


def get_dtd_columns(date_cols: Dict) -> Dict[str, str]:
    """
    Generate DtD (Day to Day) column headers
    Format: {selected_date} - {yesterday}
    """
    col_e = date_cols['E']['date']
    col_d = date_cols['D']['date']
    
    return {
        'label': f"{col_e.strftime('%d-%b-%Y')} - {col_d.strftime('%d-%b-%Y')}",
        'formula': 'E - D',
    }


def get_mom_columns(date_cols: Dict) -> Dict[str, str]:
    """
    Generate MoM (Month on Month) column headers
    Format: {selected_date} - {same_day_last_month}
    """
    col_e = date_cols['E']['date']
    col_b = date_cols['B']['date']
    
    return {
        'label': f"{col_e.strftime('%d-%b-%Y')} - {col_b.strftime('%d-%b-%Y')}",
        'formula': 'E - B',
    }


def get_mtd_columns(date_cols: Dict) -> Dict[str, str]:
    """
    Generate MtD (Month to Date) column headers
    Format: {selected_date} - {end_of_prev_month}
    """
    col_e = date_cols['E']['date']
    col_c = date_cols['C']['date']
    
    return {
        'label': f"{col_e.strftime('%d-%b-%Y')} - {col_c.strftime('%d-%b-%Y')}",
        'formula': 'E - C',
    }


def get_ytd_columns(date_cols: Dict) -> Dict[str, str]:
    """
    Generate YtD (Year to Date) column headers
    Format: {selected_date} - {end_of_same_month_last_year}
    """
    col_e = date_cols['E']['date']
    col_a = date_cols['A']['date']
    
    return {
        'label': f"{col_e.strftime('%d-%b-%Y')} - {col_a.strftime('%d-%b-%Y')}",
        'formula': 'E - A',
    }


def date_to_periode_str(d: date) -> str:
    """
    Convert date to periode string format DD/MM/YYYY
    """
    return d.strftime("%d/%m/%Y")


def get_os_for_date(queryset, target_date: date, group_by_kanca: bool = False) -> Dict:
    """
    Get OS (Outstanding) aggregated for a specific date.
    
    Args:
        queryset: Base queryset with segment and metric annotations
        target_date: Target date for OS calculation
        group_by_kanca: If True, group by kanca/kode_uker
    
    Returns:
        Dictionary with OS values
    """
    from .calculations import annotate_metrics
    from .segmentation import get_segment_annotation
    
    # Convert date to periode format (DD/MM/YYYY)
    periode_str = date_to_periode_str(target_date)
    
    # Filter by exact periode
    qs = queryset.filter(periode=periode_str)
    
    if group_by_kanca:
        # Group by kanca and sum OS
        result = {}
        qs_grouped = qs.values('kode_uker', 'uker', 'kanca').annotate(
            total_os=Sum('os')
        )
        for row in qs_grouped:
            kode = row['kode_uker']
            result[kode] = {
                'kode_uker': kode,
                'uker': row['uker'],
                'kanca': row['kanca'],
                'os': float(row['total_os'] or 0),
            }
        return result
    else:
        # Total sum
        total = qs.aggregate(total_os=Sum('os'))
        return {'total_os': float(total['total_os'] or 0)}


def calculate_table_data(
    queryset,
    selected_date: date,
    segment: str,
    table_type: str = 'KONSOL',
) -> Dict[str, Any]:
    """
    Calculate table data for a specific segment and table type.
    
    Args:
        queryset: Base LW321 queryset with annotations
        selected_date: User selected date
        segment: Segment filter (SMALL, MEDIUM, CC, KUR)
        table_type: KONSOL, KANCA_ONLY, or KCP_ONLY
    
    Returns:
        Complete table data structure
    """
    from .uker_mapping import (
        KANCA_MASTER, UKER_MASTER, KCP_CODES, KANCA_CODES,
        filter_kanca_only, filter_kcp_only, get_kanca_induk
    )
    
    # Get date columns
    date_cols = get_date_columns(selected_date)
    
    # Filter queryset by segment
    qs = queryset.filter(segment=segment)
    
    # Apply table type filter
    if table_type == 'KANCA_ONLY':
        qs = filter_kanca_only(qs)
    elif table_type == 'KCP_ONLY':
        qs = filter_kcp_only(qs)
    # KONSOL = no additional filter
    
    # Get OS for each date column
    os_data = {}
    for col_key in ['A', 'B', 'C', 'D', 'E']:
        target_date = date_cols[col_key]['date']
        os_data[col_key] = get_os_for_date(qs, target_date, group_by_kanca=True)
    
    # Build table rows
    rows = []
    totals = {
        'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0,
        'DtD': 0, 'DtD_pct': 0,
        'MoM': 0, 'MoM_pct': 0,
        'MtD': 0, 'MtD_pct': 0,
        'YtD': 0, 'YtD_pct': 0,
    }
    
    # Determine which codes to iterate
    if table_type == 'KONSOL':
        # KONSOL: Group by KANCA (sum all UKER under each KANCA)
        for kode_kanca, nama_kanca in sorted(KANCA_MASTER.items(), key=lambda x: x[1]):
            # Get all UKER codes under this KANCA
            uker_codes_under_kanca = [
                str(k) for k, (n, induk) in UKER_MASTER.items() 
                if induk == kode_kanca
            ]
            
            # Sum OS for all dates
            row_data = {
                'kode_kanca': kode_kanca,
                'kanca': nama_kanca,
                'kode_uker': '',  # Multiple UKERs
                'uker': '',  # Will show first KCP or empty
            }
            
            for col_key in ['A', 'B', 'C', 'D', 'E']:
                col_sum = sum(
                    os_data[col_key].get(code, {}).get('os', 0)
                    for code in uker_codes_under_kanca
                )
                row_data[col_key] = col_sum
                totals[col_key] += col_sum
            
            # Calculate derived columns
            row_data['DtD'] = row_data['E'] - row_data['D']
            row_data['DtD_pct'] = (row_data['DtD'] / row_data['D'] * 100) if row_data['D'] else 0
            
            row_data['MoM'] = row_data['E'] - row_data['B']
            row_data['MoM_pct'] = (row_data['MoM'] / row_data['B'] * 100) if row_data['B'] else 0
            
            row_data['MtD'] = row_data['E'] - row_data['C']
            row_data['MtD_pct'] = (row_data['MtD'] / row_data['C'] * 100) if row_data['C'] else 0
            
            row_data['YtD'] = row_data['E'] - row_data['A']
            row_data['YtD_pct'] = (row_data['YtD'] / row_data['A'] * 100) if row_data['A'] else 0
            
            rows.append(row_data)
    
    elif table_type == 'KANCA_ONLY':
        # KANCA_ONLY: Show only KANCA records
        for kode_kanca in sorted(KANCA_CODES):
            nama_kanca = KANCA_MASTER.get(kode_kanca, f"KANCA {kode_kanca}")
            kode_str = str(kode_kanca)
            
            row_data = {
                'kode_kanca': kode_kanca,
                'kanca': nama_kanca,
                'kode_uker': kode_kanca,
                'uker': nama_kanca,
            }
            
            for col_key in ['A', 'B', 'C', 'D', 'E']:
                val = os_data[col_key].get(kode_str, {}).get('os', 0)
                row_data[col_key] = val
                totals[col_key] += val
            
            # Calculate derived columns
            row_data['DtD'] = row_data['E'] - row_data['D']
            row_data['DtD_pct'] = (row_data['DtD'] / row_data['D'] * 100) if row_data['D'] else 0
            
            row_data['MoM'] = row_data['E'] - row_data['B']
            row_data['MoM_pct'] = (row_data['MoM'] / row_data['B'] * 100) if row_data['B'] else 0
            
            row_data['MtD'] = row_data['E'] - row_data['C']
            row_data['MtD_pct'] = (row_data['MtD'] / row_data['C'] * 100) if row_data['C'] else 0
            
            row_data['YtD'] = row_data['E'] - row_data['A']
            row_data['YtD_pct'] = (row_data['YtD'] / row_data['A'] * 100) if row_data['A'] else 0
            
            rows.append(row_data)
    
    elif table_type == 'KCP_ONLY':
        # KCP_ONLY: Show only KCP records
        for kode_kcp in sorted(KCP_CODES):
            if kode_kcp in UKER_MASTER:
                nama_kcp, kode_kanca_induk = UKER_MASTER[kode_kcp]
                nama_kanca = KANCA_MASTER.get(kode_kanca_induk, '')
            else:
                nama_kcp = f"KCP {kode_kcp}"
                nama_kanca = ''
                kode_kanca_induk = 0
            
            kode_str = str(kode_kcp)
            
            row_data = {
                'kode_kanca': kode_kanca_induk,
                'kanca': nama_kanca,
                'kode_uker': kode_kcp,
                'uker': nama_kcp,
            }
            
            for col_key in ['A', 'B', 'C', 'D', 'E']:
                val = os_data[col_key].get(kode_str, {}).get('os', 0)
                row_data[col_key] = val
                totals[col_key] += val
            
            # Calculate derived columns
            row_data['DtD'] = row_data['E'] - row_data['D']
            row_data['DtD_pct'] = (row_data['DtD'] / row_data['D'] * 100) if row_data['D'] else 0
            
            row_data['MoM'] = row_data['E'] - row_data['B']
            row_data['MoM_pct'] = (row_data['MoM'] / row_data['B'] * 100) if row_data['B'] else 0
            
            row_data['MtD'] = row_data['E'] - row_data['C']
            row_data['MtD_pct'] = (row_data['MtD'] / row_data['C'] * 100) if row_data['C'] else 0
            
            row_data['YtD'] = row_data['E'] - row_data['A']
            row_data['YtD_pct'] = (row_data['YtD'] / row_data['A'] * 100) if row_data['A'] else 0
            
            rows.append(row_data)
    
    # Calculate totals for derived columns
    totals['DtD'] = totals['E'] - totals['D']
    totals['DtD_pct'] = (totals['DtD'] / totals['D'] * 100) if totals['D'] else 0
    
    totals['MoM'] = totals['E'] - totals['B']
    totals['MoM_pct'] = (totals['MoM'] / totals['B'] * 100) if totals['B'] else 0
    
    totals['MtD'] = totals['E'] - totals['C']
    totals['MtD_pct'] = (totals['MtD'] / totals['C'] * 100) if totals['C'] else 0
    
    totals['YtD'] = totals['E'] - totals['A']
    totals['YtD_pct'] = (totals['YtD'] / totals['A'] * 100) if totals['A'] else 0
    
    return {
        'date_columns': date_cols,
        'dtd_header': get_dtd_columns(date_cols),
        'mom_header': get_mom_columns(date_cols),
        'mtd_header': get_mtd_columns(date_cols),
        'ytd_header': get_ytd_columns(date_cols),
        'rows': rows,
        'totals': totals,
    }


__all__ = [
    'get_date_columns',
    'get_dtd_columns',
    'get_mom_columns',
    'get_mtd_columns',
    'get_ytd_columns',
    'date_to_periode_str',
    'get_os_for_date',
    'calculate_table_data',
]
