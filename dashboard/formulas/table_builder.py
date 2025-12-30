"""Table Builder Module - Constructs KONSOL, KANCA ONLY, and KCP ONLY tables"""

from decimal import Decimal
from datetime import datetime, timedelta
from django.db.models import Sum, Q, F, Count
from ..models import LW321
from .segmentation import get_segment_annotation
from .calculations import annotate_metrics
from .uker_mapping import (
    KANCA_MASTER, UKER_MASTER, KANCA_CODES, KCP_CODES,
    get_kanca_induk, get_uker_name, get_kcp_by_kanca
)
from .komitmen_helper import (
    get_komitmen_for_month,
    get_komitmen_for_kanca_list,
    get_komitmen_value,
    check_komitmen_exists
)

def get_date_columns(selected_date):
    """
    Calculate 5 date columns (A-E) based on selected date.
    A: 31 Dec previous year | B: Same day 1 month ago | C: Last day prev month
    D: Yesterday (H-1) | E: Selected date
    """
    from dateutil.relativedelta import relativedelta
    
    year = selected_date.year
    month = selected_date.month
    
    # E: Selected date
    date_E = selected_date
    
    # D: Yesterday (H-1)
    date_D = selected_date - timedelta(days=1)
    
    # C: Last day of previous month (akhir bulan kemarin)
    first_day_this_month = datetime(year, month, 1).date()
    date_C = first_day_this_month - timedelta(days=1)
    
    # B: Same day but 1 month ago (tanggal sama bulan kemarin)
    date_B = selected_date - relativedelta(months=1)
    
    # A: 31 December of previous year (fixed December)
    date_A = datetime(year - 1, 12, 31).date()
    
    # Format labels - matching OS SMALL format
    def format_date_label(d):
        return d.strftime("%d-%b-%y")  # Format: 09-Oct-25
    
    return {
        'A': {
            'date': date_A,
            'label': f"{date_A.strftime('%b')}-{date_A.year}",  # Format: Dec-2024
            'description': f"31 Desember {date_A.year}",
        },
        'B': {
            'date': date_B,
            'label': format_date_label(date_B),
            'description': f"{date_B.day} {date_B.strftime('%B')} {date_B.year}",
        },
        'C': {
            'date': date_C,
            'label': format_date_label(date_C),
            'description': f"Akhir {date_C.strftime('%B')} {date_C.year}",
        },
        'D': {
            'date': date_D,
            'label': format_date_label(date_D),
            'description': f"H-1 ({date_D.day} {date_D.strftime('%B')} {date_D.year})",
        },
        'E': {
            'date': date_E,
            'label': format_date_label(date_E),
            'description': f"Hari ini ({date_E.day} {date_E.strftime('%B')} {date_E.year})",
        },
    }


def map_segment_and_metric_to_komitmen(segment_filter, metric_field):
    """
    Map segment_filter dan metric_field ke struktur komitmen data.
    
    Returns:
        tuple: (komitmen_segment, komitmen_metric) atau (None, None) jika tidak applicable
        
    Mapping:
    - Segment: 'SMALL' â†’ 'small', 'CC' â†’ 'cc', 'SMALL NCC' â†’ 'ncc', 'KUR' â†’ 'kur'
    - Metric: 'os' â†’ 'os', 'nsb' â†’ 'deb', 'dpk' â†’ 'dpk', dll
    """
    # Map segment filter
    segment_map = {
        'SMALL': 'small',  # SMALL aggregate (will be handled specially)
        'SMALL NCC': 'ncc',
        'CC': 'cc',
        'KUR': 'kur',
        'MEDIUM': None,  # MEDIUM tidak ada di komitmen
    }
    
    komitmen_segment = segment_map.get(segment_filter)
    
    if not komitmen_segment:
        return None, None
    
    # Map metric field
    # Mapping sesuai grouping:
    # DEB = Kolom E J O T
    # OS = Kolom F K P U
    # PL = Kolom G L Q V
    # NPL = Kolom H M R W
    # DPK = Kolom I N S X
    metric_map = {
        'os': 'os',
        'nsb': 'deb',  # NSB (debitur) maps to DEB column
        'dpk': 'dpk',
        'sml': 'dpk',  # SML also maps to DPK
        'npl': 'npl',
        'dpk_pct': 'dpk',  # For percentage, use DPK value
        'npl_pct': 'npl',  # For percentage, use NPL value
        'lar': 'pl',  # LAR (Lancar) maps to PL
    }
    
    komitmen_metric = metric_map.get(metric_field)
    
    return komitmen_segment, komitmen_metric



# ============================================================================
# Core Query Functions
# ============================================================================

def get_base_queryset(target_date, segment_filter, metric_field='os', kol_adk_filter=None):
    """
    Get base queryset with filters and annotations.
    
    Args:
        target_date: Date to filter data
        segment_filter: Segment to filter (e.g., 'SMALL', 'MEDIUM', 'CC', 'KUR')
                       - 'SMALL' = Aggregate of SMALL NCC + CC + KUR (all non-MEDIUM)
                       - 'MEDIUM' = Only MEDIUM segment
                       - 'CC', 'KUR', 'SMALL NCC' = Specific segments
        metric_field: Field to aggregate (e.g., 'os', 'dpk', 'npl', 'lar')
        kol_adk_filter: Optional filter for kol_adk field (e.g., '2' for DPK)
    
    Returns:
        QuerySet: Annotated and filtered queryset
    """
    qs = LW321.objects.filter(periode=target_date.strftime('%d/%m/%Y'))
    qs = qs.annotate(segment=get_segment_annotation())
    qs = annotate_metrics(qs)
    
    if segment_filter:
        # SMALL is an aggregate segment = SMALL NCC + CC + KUR (all non-MEDIUM)
        if segment_filter == 'SMALL':
            qs = qs.exclude(segment='MEDIUM')
        else:
            qs = qs.filter(segment=segment_filter)
    
    # Apply kol_adk filter if specified (for DPK: kol_adk='2')
    if kol_adk_filter is not None:
        qs = qs.filter(kol_adk=kol_adk_filter)
    
    return qs


def calculate_percentage_metric(metric_value, base_value):
    """
    Calculate percentage metric (metric / base * 100).
    Used for %DPK and %NPL calculations.
    
    Args:
        metric_value: Numerator value (dpk or npl)
        base_value: Denominator value (usually os)
    
    Returns:
        float: Percentage value (0-100)
    """
    if base_value == 0 or base_value is None:
        return 0
    if metric_value is None:
        return 0
    return (metric_value / base_value) * 100


def get_metric_by_uker(target_date, segment_filter, metric_field='os', kol_adk_filter=None):
    """
    Get metric sum grouped by UKER.
    Handles special percentage metrics (dpk_pct, npl_pct) and NSB (customer count).
    
    DPK Logic:
    - DPK = SUM(kolektibilitas_dpk) 
    - No kol_adk filter needed, DPK is already its own column
    
    NSB Logic:
    - NSB = SUM(NASABAH) WHERE DUB_NASABAH='TRUE'
    - Filter: segment and dub_nasabah='TRUE'
    
    Args:
        kol_adk_filter: Optional filter for kol_adk field (not used for DPK)
    
    Returns:
        dict: {kode_uker: metric_value}
    """
    qs = get_base_queryset(target_date, segment_filter, metric_field, kol_adk_filter)
    
    # Handle NSB (customer count) specially
    if metric_field == 'nsb':
        # Sum NASABAH column per UKER where DUB_NASABAH='TRUE' (case-insensitive)
        from django.db.models import Q
        result = qs.filter(
            Q(dub_nasabah__iexact='TRUE')  # Case-insensitive: 'TRUE', 'True', 'true'
        ).values('kode_uker').annotate(
            total=Sum('nasabah')
        ).order_by('kode_uker')
        
        # Convert to Decimal for consistency with other metrics
        return {item['kode_uker']: Decimal(str(item['total'] or 0)) for item in result}
    
    # Handle percentage metrics specially
    elif metric_field == 'dpk_pct':
        # %DPK = (DPK where kol_adk='2' / OS all kol_adk) * 100
        # IMPORTANT: DPK uses kol_adk='2', but OS uses all kol_adk
        # This measures what % of total portfolio is DPK
        
        # Get DPK values (with kol_adk='2' filter)
        qs_dpk = get_base_queryset(target_date, segment_filter, 'sml', kol_adk_filter='2')
        dpk_by_uker = qs_dpk.values('kode_uker').annotate(
            dpk_sum=Sum('os')  # Use OS field directly with kol_adk='2' filter
        ).order_by('kode_uker')
        
        # Get OS values (without kol_adk filter - all portfolio)
        qs_os = get_base_queryset(target_date, segment_filter, 'os', kol_adk_filter=None)
        os_by_uker = qs_os.values('kode_uker').annotate(
            os_sum=Sum('os')
        ).order_by('kode_uker')
        
        # Build dictionaries
        dpk_dict = {item['kode_uker']: item['dpk_sum'] or Decimal('0') for item in dpk_by_uker}
        os_dict = {item['kode_uker']: item['os_sum'] or Decimal('0') for item in os_by_uker}
        
        # Calculate percentage for each UKER
        result = {}
        all_uker_codes = set(dpk_dict.keys()) | set(os_dict.keys())
        for kode_uker in all_uker_codes:
            dpk_val = dpk_dict.get(kode_uker, Decimal('0'))
            os_val = os_dict.get(kode_uker, Decimal('0'))
            result[kode_uker] = calculate_percentage_metric(dpk_val, os_val)
        
        return result
    
    elif metric_field == 'npl_pct':
        # %NPL = (NPL where kol_adk IN ('3','4','5') / OS all kol_adk) * 100
        # IMPORTANT: NPL uses kol_adk IN ('3','4','5'), but OS uses all kol_adk
        # This measures what % of total portfolio is NPL
        
        # Get NPL values (npl annotation already filters kol_adk IN ('3','4','5'))
        # But for clarity, we'll use explicit filter
        qs_npl = get_base_queryset(target_date, segment_filter, 'npl', kol_adk_filter=None)
        # Filter for NPL kol_adk manually since annotation handles it
        npl_by_uker = qs_npl.values('kode_uker').annotate(
            npl_sum=Sum('npl')  # npl annotation already has the filter
        ).order_by('kode_uker')
        
        # Get OS values (without kol_adk filter - all portfolio)
        qs_os = get_base_queryset(target_date, segment_filter, 'os', kol_adk_filter=None)
        os_by_uker = qs_os.values('kode_uker').annotate(
            os_sum=Sum('os')
        ).order_by('kode_uker')
        
        # Build dictionaries
        npl_dict = {item['kode_uker']: item['npl_sum'] or Decimal('0') for item in npl_by_uker}
        os_dict = {item['kode_uker']: item['os_sum'] or Decimal('0') for item in os_by_uker}
        
        # Calculate percentage for each UKER
        result = {}
        all_uker_codes = set(npl_dict.keys()) | set(os_dict.keys())
        for kode_uker in all_uker_codes:
            npl_val = npl_dict.get(kode_uker, Decimal('0'))
            os_val = os_dict.get(kode_uker, Decimal('0'))
            result[kode_uker] = calculate_percentage_metric(npl_val, os_val)
        
        return result
    
    else:
        # Regular metrics (os, npl, lar, lr, sml/dpk, etc.)
        # For DPK, use 'sml' field which is already annotated in calculations.py
        # SML = DPK + (Lancar if kol_adk == '2')
        actual_field = 'sml' if metric_field == 'dpk' else metric_field
        
        result = qs.values('kode_uker').annotate(
            total=Sum(actual_field)
        ).order_by('kode_uker')
        
        return {item['kode_uker']: item['total'] or Decimal('0') for item in result}


def get_kode_kanca_from_uker(kode_uker_str):
    """
    Determine the parent KANCA code from a given UKER code.
    Returns integer kode_kanca or None.
    """
    try:
        kode_uker_int = int(kode_uker_str)
    except (ValueError, TypeError):
        # If string code, check directly in KANCA_CODES
        if kode_uker_str in [str(k) for k in KANCA_CODES]:
            return kode_uker_str
        return None
    
    # Check if it's a KANCA
    if kode_uker_int in KANCA_CODES:
        return kode_uker_int
    
    # Check if it's in UKER_MASTER (could be KCP)
    if kode_uker_int in UKER_MASTER:
        _, kode_kanca_induk = UKER_MASTER[kode_uker_int]
        return kode_kanca_induk
    
    # Try with get_kanca_induk helper from uker_mapping
    return get_kanca_induk(kode_uker_int)


def get_metric_by_kanca(target_date, segment_filter, metric_field='os', kol_adk_filter=None):
    """
    Get metric sum grouped by parent KANCA (dynamically calculated).
    
    This sums values from all UKERs under each KANCA.
    For all metrics (OS, DPK, NPL, LAR, LR, NSB), we sum the values from each UKER
    that belongs to the KANCA induk.
    
    Formula: KONSOL = KANCA ONLY + KCP ONLY (must be valid for all metrics)
    
    Args:
        kol_adk_filter: Optional filter for kol_adk field
    
    Returns:
        dict: {kode_kanca: metric_value}
    """
    metric_by_uker = get_metric_by_uker(target_date, segment_filter, metric_field, kol_adk_filter)
    metric_by_kanca = {}
    
    for kode_uker_str, value in metric_by_uker.items():
        kode_kanca = get_kode_kanca_from_uker(kode_uker_str)
        if kode_kanca:
            if kode_kanca not in metric_by_kanca:
                metric_by_kanca[kode_kanca] = Decimal('0')
            metric_by_kanca[kode_kanca] += value
    
    return metric_by_kanca


# ============================================================================
# Table Building Functions
# ============================================================================

def calculate_changes(A, B, C, D, E):
    """
    Calculate DtD, MoM, MtD, YtD and their percentages.
    
    Note: Jika nilai pembanding (A/B/C/D) adalah None atau 0, tetap hitung perubahan.
    Contoh: E=100, A=None -> YtD=100 (bukan 0)
            E=None, A=100 -> YtD=-100 (bukan 0)
    """
    def safe_divide(num, den):
        if den == 0 or den is None:
            return Decimal('0')
        return (num / den) * Decimal('100')
    
    # Convert None to 0 for calculation
    E_val = E if E is not None else Decimal('0')
    D_val = D if D is not None else Decimal('0')
    B_val = B if B is not None else Decimal('0')
    C_val = C if C is not None else Decimal('0')
    A_val = A if A is not None else Decimal('0')
    
    # Calculate changes (always calculate even if one side is 0/None)
    DtD = E_val - D_val
    DtD_pct = safe_divide(DtD, D_val) if D_val != 0 else Decimal('0')
    
    MoM = E_val - B_val
    MoM_pct = safe_divide(MoM, B_val) if B_val != 0 else Decimal('0')
    
    MtD = E_val - C_val
    MtD_pct = safe_divide(MtD, C_val) if C_val != 0 else Decimal('0')
    
    YtD = E_val - A_val
    YtD_pct = safe_divide(YtD, A_val) if A_val != 0 else Decimal('0')
    
    return {
        'DtD': DtD,
        'DtD_pct': DtD_pct,
        'MoM': MoM,
        'MoM_pct': MoM_pct,
        'MtD': MtD,
        'MtD_pct': MtD_pct,
        'YtD': YtD,
        'YtD_pct': YtD_pct,
    }


def build_konsol_table(date_columns, segment_filter='SMALL', metric_field='os', kol_adk_filter=None):
    """
    Build KONSOL table (grouped by KANCA - includes both KANCA and their KCPs).
    
    For percentage metrics (dpk_pct, npl_pct):
    - Each row shows: (SUM DPK for KANCA+KCP) / (SUM OS for KANCA+KCP) Ã— 100
    - Total row shows: (SUM DPK all) / (SUM OS all) Ã— 100
    
    Args:
        kol_adk_filter: Optional filter for kol_adk field (e.g., '2' for DPK)
    """
    rows = []
    
    # Get selected date for komitmen lookup (date E)
    selected_date = date_columns['E']['date']
    year = selected_date.year
    month = selected_date.month
    
    # Get komitmen data for the selected month
    komitmen_segment, komitmen_metric = map_segment_and_metric_to_komitmen(segment_filter, metric_field)
    komitmen_data = None
    
    if komitmen_segment and komitmen_metric:
        # Check if komitmen exists for this month
        if check_komitmen_exists(year, month):
            komitmen_data = get_komitmen_for_kanca_list(year, month)
    
    # For percentage metrics, we need raw data (DPK/NPL and OS) instead of pre-calculated percentages
    if metric_field in ['dpk_pct', 'npl_pct']:
        # Determine which raw metrics to use and their filters
        if metric_field == 'dpk_pct':
            metric_raw = 'sml'  # DPK
            base_raw = 'os'     # OS
            # IMPORTANT: For %DPK calculation:
            # - DPK uses kol_adk='2' filter
            # - OS uses ALL kol_adk (no filter)
            # This measures what % of TOTAL portfolio is DPK
            metric_filter = '2'
            base_filter = None   # OS includes all kol_adk
        elif metric_field == 'npl_pct':
            metric_raw = 'npl'  # NPL
            base_raw = 'os'     # OS
            metric_filter = None  # NPL uses kol_adk 3,4,5 (handled in annotation)
            base_filter = None    # OS for NPL uses all kol_adk
        
        # Get raw data for each date
        metric_data_by_date = {}
        os_data_by_date = {}
        for col_name, col_info in date_columns.items():
            metric_data_by_date[col_name] = get_metric_by_kanca(
                col_info['date'], segment_filter, metric_raw, metric_filter
            )
            os_data_by_date[col_name] = get_metric_by_kanca(
                col_info['date'], segment_filter, base_raw, base_filter
            )
        
        # Build rows for each KANCA
        for idx, kode_kanca in enumerate(KANCA_CODES, start=1):
            kanca_name = KANCA_MASTER.get(kode_kanca, f"KANCA {kode_kanca}")
            
            # Get raw metric (DPK or NPL) for each date
            metric_A = metric_data_by_date['A'].get(kode_kanca, Decimal('0'))
            metric_B = metric_data_by_date['B'].get(kode_kanca, Decimal('0'))
            metric_C = metric_data_by_date['C'].get(kode_kanca, Decimal('0'))
            metric_D = metric_data_by_date['D'].get(kode_kanca, Decimal('0'))
            metric_E = metric_data_by_date['E'].get(kode_kanca, Decimal('0'))
            
            # Get OS for each date
            os_A = os_data_by_date['A'].get(kode_kanca, Decimal('0'))
            os_B = os_data_by_date['B'].get(kode_kanca, Decimal('0'))
            os_C = os_data_by_date['C'].get(kode_kanca, Decimal('0'))
            os_D = os_data_by_date['D'].get(kode_kanca, Decimal('0'))
            os_E = os_data_by_date['E'].get(kode_kanca, Decimal('0'))
            
            # Calculate percentage for each date
            A = calculate_percentage_metric(metric_A, os_A)
            B = calculate_percentage_metric(metric_B, os_B)
            C = calculate_percentage_metric(metric_C, os_C)
            D = calculate_percentage_metric(metric_D, os_D)
            E = calculate_percentage_metric(metric_E, os_E)
            
            changes = calculate_changes(A, B, C, D, E)
            
            # Get komitmen value untuk kanca ini
            # kode_kanca di komitmen_data sekarang integer (IntegerField), tidak perlu str()
            komitmen_value = None
            if komitmen_data and komitmen_segment and komitmen_metric:
                # SPECIAL CASE for %DPK/%NPL: Calculate komitmen as percentage
                if metric_field in ['dpk_pct', 'npl_pct']:
                    # Get raw komitmen for numerator (DPK or NPL)
                    komitmen_raw = get_komitmen_value(komitmen_data, kode_kanca, komitmen_segment, komitmen_metric)
                    # Get komitmen OS for denominator
                    komitmen_os = get_komitmen_value(komitmen_data, kode_kanca, komitmen_segment, 'os')
                    
                    # Calculate percentage: (DPK/NPL / OS) Ã— 100
                    if komitmen_raw is not None and komitmen_os is not None and komitmen_os != 0:
                        komitmen_value = calculate_percentage_metric(komitmen_raw, komitmen_os)
                    else:
                        komitmen_value = None
                else:
                    # For other metrics: Use raw komitmen value
                    komitmen_value = get_komitmen_value(komitmen_data, kode_kanca, komitmen_segment, komitmen_metric)
            
            # Calculate komitmen % Achievement and Gap
            # % Ach Formula: =IFERROR(IF((E/Komitmen)>1.1,110%,IF((E/Komitmen)<0,0%,(E/Komitmen))),110%)
            # Gap Formula: E - Komitmen
            # SPECIAL CASE for DPK/NPL/DPK_PCT/NPL_PCT: Reversed formula (Komitmen / E) instead of (E / Komitmen)
            komitmen_pct_ach = None
            komitmen_gab_real = None
            if komitmen_value is not None and komitmen_value != 0:
                # For DPK/NPL and %DPK/%NPL pages: Use reversed formula (Komitmen / E) Ã— 100
                if metric_field in ['dpk', 'npl', 'dpk_pct', 'npl_pct']:
                    if E != 0:
                        ratio = komitmen_value / E  # REVERSED: Komitmen / E
                    else:
                        ratio = Decimal('11')  # Will result in 110% cap
                else:
                    # For OS and other metrics: Normal formula (E / Komitmen)
                    ratio = E / komitmen_value
                
                if ratio > Decimal('1.1'):
                    komitmen_pct_ach = Decimal('110')
                elif ratio < 0:
                    komitmen_pct_ach = Decimal('0')
                else:
                    komitmen_pct_ach = ratio * Decimal('100')
                
                # Gap = E - Komitmen (positive = surplus, negative = shortfall)
                komitmen_gab_real = E - komitmen_value
            
            rows.append({
                'no': idx,
                'kode_kanca': kode_kanca,
                'kanca': kanca_name,
                'A': A,
                'B': B,
                'C': C,
                'D': D,
                'E': E,
                **changes,
                # Komitmen columns
                'komitmen': komitmen_value,
                'komitmen_pct_ach': komitmen_pct_ach,
                'komitmen_gab_real': komitmen_gab_real,
            })
    else:
        # For non-percentage metrics, use existing logic
        # Get data for each date
        data_by_date = {}
        for col_name, col_info in date_columns.items():
            data_by_date[col_name] = get_metric_by_kanca(
                col_info['date'], 
                segment_filter, 
                metric_field,
                kol_adk_filter
            )
        
        # Build rows for each KANCA
        for idx, kode_kanca in enumerate(KANCA_CODES, start=1):
            kanca_name = KANCA_MASTER.get(kode_kanca, f"KANCA {kode_kanca}")
            
            A = data_by_date['A'].get(kode_kanca, Decimal('0'))
            B = data_by_date['B'].get(kode_kanca, Decimal('0'))
            C = data_by_date['C'].get(kode_kanca, Decimal('0'))
            D = data_by_date['D'].get(kode_kanca, Decimal('0'))
            E = data_by_date['E'].get(kode_kanca, Decimal('0'))
            
            changes = calculate_changes(A, B, C, D, E)
            
            # Get komitmen value untuk kanca ini
            # kode_kanca di komitmen_data sekarang integer (IntegerField), tidak perlu str()
            komitmen_value = None
            if komitmen_data and komitmen_segment and komitmen_metric:
                komitmen_value = get_komitmen_value(komitmen_data, kode_kanca, komitmen_segment, komitmen_metric)
            
            # Calculate komitmen % Achievement and Gap
            # % Ach Formula: =IFERROR(IF((E/Komitmen)>1.1,110%,IF((E/Komitmen)<0,0%,(E/Komitmen))),110%)
            # Gap Formula: E - Komitmen (positive = surplus, negative = shortfall)
            # NOTE: E dari database dalam RUPIAH PENUH, komitmen dalam RIBUAN (juta rupiah)
            # Konversi E ke RIBUAN (juta) terlebih dahulu untuk consistency
            # SPECIAL CASE for DPK/NPL: Reversed formula (Komitmen / E) instead of (E / Komitmen)
            komitmen_pct_ach = None
            komitmen_gab_real = None
            if komitmen_value is not None and komitmen_value != 0:
                E_in_millions = E / Decimal('1000000')  # Convert E from rupiah to millions (thousands)
                
                # For DPK/NPL pages: Use reversed formula (Komitmen / E) Ã— 100
                if metric_field in ['dpk', 'npl']:
                    if E_in_millions != 0:
                        ratio = komitmen_value / E_in_millions  # REVERSED: Komitmen / E
                    else:
                        ratio = Decimal('11')  # Will result in 110% cap
                else:
                    # For OS and other metrics: Normal formula (E / Komitmen)
                    ratio = E_in_millions / komitmen_value
                
                if ratio > Decimal('1.1'):
                    # Cap at 110%
                    komitmen_pct_ach = Decimal('110')
                elif ratio < 0:
                    # Floor at 0%
                    komitmen_pct_ach = Decimal('0')
                else:
                    # Normal calculation
                    komitmen_pct_ach = ratio * Decimal('100')
                
                # Gap = E - Komitmen (both in millions/thousands)
                # Positive = surplus (realisasi > komitmen) â†’ hitam
                # Negative = shortfall (realisasi < komitmen) â†’ merah
                komitmen_gab_real = E_in_millions - komitmen_value
            
            rows.append({
                'no': idx,
                'kode_kanca': kode_kanca,
                'kanca': kanca_name,
                'A': A,
                'B': B,
                'C': C,
                'D': D,
                'E': E,
                **changes,
                # Komitmen value
                'komitmen': komitmen_value,
                'komitmen_pct_ach': komitmen_pct_ach,
                'komitmen_gab_real': komitmen_gab_real,
            })
    
    # Calculate totals
    # For percentage metrics (dpk_pct, npl_pct), we need to recalculate from raw data
    # Total %DPK = (Total DPK / Total OS) Ã— 100, NOT sum of individual percentages
    if metric_field in ['dpk_pct', 'npl_pct']:
        # Get raw metric and base (OS) data for each date
        if metric_field == 'dpk_pct':
            # Need DPK (sml) and OS
            metric_raw = 'sml'
            base_raw = 'os'
            metric_filter = '2'   # DPK uses kol_adk='2'
            base_filter = None    # OS uses all kol_adk
        elif metric_field == 'npl_pct':
            # Need NPL and OS
            metric_raw = 'npl'
            base_raw = 'os'
            metric_filter = None
            base_filter = None
        
        # Get totals for each date
        totals = {}
        for col_name, col_info in date_columns.items():
            # Get metric sum (DPK or NPL)
            metric_data = get_metric_by_kanca(col_info['date'], segment_filter, metric_raw, metric_filter)
            metric_sum = sum(metric_data.values())
            
            # Get OS sum (all kol_adk)
            os_data = get_metric_by_kanca(col_info['date'], segment_filter, base_raw, base_filter)
            os_sum = sum(os_data.values())
            
            # Calculate percentage
            totals[col_name] = calculate_percentage_metric(metric_sum, os_sum)
    else:
        # For non-percentage metrics, simple sum works
        totals = {
            'A': sum(row['A'] for row in rows),
            'B': sum(row['B'] for row in rows),
            'C': sum(row['C'] for row in rows),
            'D': sum(row['D'] for row in rows),
            'E': sum(row['E'] for row in rows),
        }
    
    totals.update(calculate_changes(
        totals['A'], totals['B'], totals['C'], totals['D'], totals['E']
    ))
    
    # Calculate komitmen total
    komitmen_total = None
    komitmen_pct_ach_total = None
    komitmen_gab_real_total = None
    
    if komitmen_data:
        # SPECIAL CASE for %DPK/%NPL: Calculate komitmen total as percentage
        if metric_field in ['dpk_pct', 'npl_pct']:
            # Get all kanca codes from rows
            kanca_codes = [row['kode_kanca'] for row in rows]
            
            # Sum raw komitmen for numerator (DPK or NPL)
            komitmen_raw_sum = Decimal('0')
            for kode_kanca in kanca_codes:
                komitmen_raw = get_komitmen_value(komitmen_data, kode_kanca, komitmen_segment, komitmen_metric)
                if komitmen_raw:
                    komitmen_raw_sum += komitmen_raw
            
            # Sum komitmen OS for denominator
            komitmen_os_sum = Decimal('0')
            for kode_kanca in kanca_codes:
                komitmen_os = get_komitmen_value(komitmen_data, kode_kanca, komitmen_segment, 'os')
                if komitmen_os:
                    komitmen_os_sum += komitmen_os
            
            # Calculate total percentage: (Total DPK/NPL / Total OS) Ã— 100
            if komitmen_os_sum != 0:
                komitmen_total = calculate_percentage_metric(komitmen_raw_sum, komitmen_os_sum)
            else:
                komitmen_total = None
        else:
            # For other metrics: Sum all komitmen values from rows
            komitmen_values = [row['komitmen'] for row in rows if row['komitmen'] is not None]
            if komitmen_values:
                komitmen_total = sum(komitmen_values)
            
        # Calculate total % Achievement and Gap
        if komitmen_total is not None and komitmen_total != 0:
            # For percentage metrics (dpk_pct, npl_pct), totals['E'] is already a percentage
            # For other metrics, totals['E'] is in RUPIAH PENUH, need conversion to millions
            if metric_field in ['dpk_pct', 'npl_pct']:
                E_value = totals['E']  # Already a percentage
            else:
                E_value = totals['E'] / Decimal('1000000')  # Convert to millions
            
            # For DPK/NPL and %DPK/%NPL pages: Use reversed formula (Komitmen / E) Ã— 100
            if metric_field in ['dpk', 'npl', 'dpk_pct', 'npl_pct']:
                if E_value != 0:
                    komitmen_pct_ach_total = (komitmen_total / E_value) * Decimal('100')
                else:
                    komitmen_pct_ach_total = Decimal('110')  # IFERROR result
            else:
                # For OS and other metrics: Normal formula (E / Komitmen)
                komitmen_pct_ach_total = (E_value / komitmen_total) * Decimal('100')
                
            # Cap at 110%
            if komitmen_pct_ach_total > Decimal('110'):
                komitmen_pct_ach_total = Decimal('110')
            # Floor at 0%
            elif komitmen_pct_ach_total < Decimal('0'):
                komitmen_pct_ach_total = Decimal('0')
            # Gap thd Realisasi = E - Komitmen (both in same unit)
            komitmen_gab_real_total = E_value - komitmen_total
        else:
            # IFERROR: if komitmen is 0, return 110%
            komitmen_pct_ach_total = Decimal('110')
            if metric_field in ['dpk_pct', 'npl_pct']:
                E_value = totals['E']
            else:
                E_value = totals['E'] / Decimal('1000000')
            komitmen_gab_real_total = E_value
    
    totals['komitmen'] = komitmen_total
    totals['komitmen_pct_ach'] = komitmen_pct_ach_total
    totals['komitmen_gab_real'] = komitmen_gab_real_total
    
    return {
        'title': f'TOTAL {metric_field.upper()} {segment_filter} KANCA KONSOL',
        'rows': rows,
        'totals': totals
    }


def build_kanca_only_table(date_columns, segment_filter='SMALL', metric_field='os', kol_adk_filter=None):
    """
    Build KANCA ONLY table (only KANCA, excluding KCPs).
    Only includes actual KANCA codes, not KCP contributions.
    
    Args:
        kol_adk_filter: Optional filter for kol_adk field (e.g., '2' for DPK)
    """
    rows = []
    
    # Get selected date for komitmen lookup (date E)
    selected_date = date_columns['E']['date']
    year = selected_date.year
    month = selected_date.month
    
    # Get komitmen data for the selected month (per uker)
    komitmen_segment, komitmen_metric = map_segment_and_metric_to_komitmen(segment_filter, metric_field)
    komitmen_data = None
    
    if komitmen_segment and komitmen_metric:
        # Check if komitmen exists for this month
        if check_komitmen_exists(year, month):
            komitmen_data = get_komitmen_for_month(year, month)  # Per uker data
    
    # Initialize totals
    totals = {
        'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0,
        'DtD': 0, 'MoM': 0, 'MtD': 0, 'YtD': 0,
        'DtD_pct': 0, 'MoM_pct': 0, 'MtD_pct': 0, 'YtD_pct': 0
    }
    
    # Pre-fetch all metrics for all dates (optimization)
    # This avoids calling get_metric_by_uker() inside the loop
    metrics_by_date = {}
    for col_name, col_info in date_columns.items():
        metrics_by_date[col_name] = get_metric_by_uker(
            col_info['date'],
            segment_filter,
            metric_field,
            kol_adk_filter
        )
    
    for idx, kode_kanca in enumerate(KANCA_CODES, start=1):
        # Get metrics for each date column - only for KANCA code itself
        # Convert kode_kanca to string because kode_uker in database is CharField
        kode_kanca_str = str(kode_kanca)
        
        A_val = metrics_by_date['A'].get(kode_kanca_str, 0)
        B_val = metrics_by_date['B'].get(kode_kanca_str, 0)
        C_val = metrics_by_date['C'].get(kode_kanca_str, 0)
        D_val = metrics_by_date['D'].get(kode_kanca_str, 0)
        E_val = metrics_by_date['E'].get(kode_kanca_str, 0)
        
        # Calculate changes
        changes = calculate_changes(A_val, B_val, C_val, D_val, E_val)
        
        # Get komitmen value untuk kanca ini (using kode_uker = kode_kanca untuk KANCA ONLY)
        komitmen_value = None
        if komitmen_data and komitmen_segment and komitmen_metric:
            # SPECIAL CASE for %DPK/%NPL: Calculate komitmen as percentage
            if metric_field in ['dpk_pct', 'npl_pct']:
                # Get raw komitmen for numerator (DPK or NPL)
                komitmen_raw = get_komitmen_value(komitmen_data, kode_kanca_str, komitmen_segment, komitmen_metric)
                # Get komitmen OS for denominator
                komitmen_os = get_komitmen_value(komitmen_data, kode_kanca_str, komitmen_segment, 'os')
                
                # Calculate percentage: (DPK/NPL / OS) Ã— 100
                if komitmen_raw is not None and komitmen_os is not None and komitmen_os != 0:
                    komitmen_value = calculate_percentage_metric(komitmen_raw, komitmen_os)
                else:
                    komitmen_value = None
            else:
                # For other metrics: Use raw komitmen value
                komitmen_value = get_komitmen_value(komitmen_data, kode_kanca_str, komitmen_segment, komitmen_metric)
        
        # Calculate komitmen % Achievement and Gap
        # % Ach Formula: =IFERROR(IF((E/Komitmen)>1.1,110%,IF((E/Komitmen)<0,0%,(E/Komitmen))),110%)
        # Gap Formula: E - Komitmen (positive = surplus, negative = shortfall)
        # NOTE: E_val dari database dalam RUPIAH PENUH, komitmen dalam RIBUAN (juta rupiah)
        # SPECIAL CASE for DPK/NPL/DPK_PCT/NPL_PCT: Reversed formula (Komitmen / E) instead of (E / Komitmen)
        komitmen_pct_ach = None
        komitmen_gab_real = None
        if komitmen_value is not None and komitmen_value != 0:
            # For percentage metrics (dpk_pct, npl_pct), E_val is already a percentage
            # For other metrics, E_val is in RUPIAH PENUH, need conversion to millions
            if metric_field in ['dpk_pct', 'npl_pct']:
                E_value = E_val  # Already a percentage
            else:
                E_value = E_val / Decimal('1000000')  # Convert to millions
            
            # For DPK/NPL and %DPK/%NPL pages: Use reversed formula (Komitmen / E) Ã— 100
            if metric_field in ['dpk', 'npl', 'dpk_pct', 'npl_pct']:
                if E_value != 0:
                    ratio = komitmen_value / E_value  # REVERSED: Komitmen / E
                else:
                    ratio = Decimal('11')  # Will result in 110% cap
            else:
                # For OS and other metrics: Normal formula (E / Komitmen)
                ratio = E_value / komitmen_value
            
            if ratio > Decimal('1.1'):
                komitmen_pct_ach = Decimal('110')
            elif ratio < 0:
                komitmen_pct_ach = Decimal('0')
            else:
                komitmen_pct_ach = ratio * Decimal('100')
            
            # Gap = E - Komitmen (both in same unit)
            # Positive = surplus (realisasi > komitmen) â†’ hitam (for DPK/NPL reversed to red)
            # Negative = shortfall (realisasi < komitmen) â†’ merah (for DPK/NPL reversed to black)
            komitmen_gab_real = E_value - komitmen_value
        
        # Build row
        kanca_name = KANCA_MASTER.get(kode_kanca, f"KANCA {kode_kanca}")
        row = {
            'no': idx,
            'kode_kanca': kode_kanca,
            'kanca': kanca_name,
            'kode_uker': kode_kanca,  # For KANCA ONLY, kode_uker = kode_kanca
            'uker': kanca_name,        # For KANCA ONLY, uker name = kanca name
            'A': A_val,
            'B': B_val,
            'C': C_val,
            'D': D_val,
            'E': E_val,
            'DtD': changes['DtD'],
            'DtD_pct': changes['DtD_pct'],
            'MoM': changes['MoM'],
            'MoM_pct': changes['MoM_pct'],
            'MtD': changes['MtD'],
            'MtD_pct': changes['MtD_pct'],
            'YtD': changes['YtD'],
            'YtD_pct': changes['YtD_pct'],
            # Komitmen value
            'komitmen': komitmen_value,
            'komitmen_pct_ach': komitmen_pct_ach,
            'komitmen_gab_real': komitmen_gab_real,
        }
        rows.append(row)
        
        # Add to totals
        totals['A'] += A_val
        totals['B'] += B_val
        totals['C'] += C_val
        totals['D'] += D_val
        totals['E'] += E_val
    
    # Calculate totals changes
    # For percentage metrics, recalculate from raw data instead of summing percentages
    if metric_field in ['dpk_pct', 'npl_pct']:
        # Determine which raw metrics to use
        if metric_field == 'dpk_pct':
            metric_raw = 'sml'
            base_raw = 'os'
            metric_filter = '2'   # DPK uses kol_adk='2'
            base_filter = None    # OS uses all kol_adk
        elif metric_field == 'npl_pct':
            metric_raw = 'npl'
            base_raw = 'os'
            metric_filter = None
            base_filter = None
        
        # Recalculate totals for each date from raw data
        totals_recalc = {}
        for col_name, col_info in date_columns.items():
            # Get metric sum (DPK or NPL) - only KANCA codes
            metric_data = get_metric_by_uker(col_info['date'], segment_filter, metric_raw, metric_filter)
            metric_sum = sum(v for k, v in metric_data.items() if str(k) in [str(kc) for kc in KANCA_CODES])
            
            # Get OS sum - only KANCA codes, all kol_adk
            os_data = get_metric_by_uker(col_info['date'], segment_filter, base_raw, base_filter)
            os_sum = sum(v for k, v in os_data.items() if str(k) in [str(kc) for kc in KANCA_CODES])
            
            # Calculate percentage
            totals_recalc[col_name] = calculate_percentage_metric(metric_sum, os_sum)
        
        # Replace totals with recalculated values
        totals['A'] = totals_recalc['A']
        totals['B'] = totals_recalc['B']
        totals['C'] = totals_recalc['C']
        totals['D'] = totals_recalc['D']
        totals['E'] = totals_recalc['E']
    
    totals_changes = calculate_changes(
        totals['A'], totals['B'], totals['C'], totals['D'], totals['E']
    )
    totals.update(totals_changes)
    
    # Calculate komitmen total
    komitmen_total = None
    komitmen_pct_ach_total = None
    komitmen_gab_real_total = None
    
    if komitmen_data:
        # SPECIAL CASE for %DPK/%NPL: Calculate komitmen total as percentage
        if metric_field in ['dpk_pct', 'npl_pct']:
            # Get all uker codes from rows (KANCA codes only)
            # Convert to string because komitmen_dict keys are strings (kode_uker is CharField)
            uker_codes = [str(row['kode_uker']) for row in rows]
            
            # Sum raw komitmen for numerator (DPK or NPL)
            komitmen_raw_sum = Decimal('0')
            for kode_uker in uker_codes:
                komitmen_raw = get_komitmen_value(komitmen_data, kode_uker, komitmen_segment, komitmen_metric)
                if komitmen_raw:
                    komitmen_raw_sum += komitmen_raw
            
            # Sum komitmen OS for denominator
            komitmen_os_sum = Decimal('0')
            for kode_uker in uker_codes:
                komitmen_os = get_komitmen_value(komitmen_data, kode_uker, komitmen_segment, 'os')
                if komitmen_os:
                    komitmen_os_sum += komitmen_os
            
            # Calculate total percentage: (Total DPK/NPL / Total OS) Ã— 100
            if komitmen_os_sum != 0:
                komitmen_total = calculate_percentage_metric(komitmen_raw_sum, komitmen_os_sum)
            else:
                komitmen_total = None
        else:
            # For other metrics: Sum all komitmen values from rows
            komitmen_values = [row['komitmen'] for row in rows if row['komitmen'] is not None]
            if komitmen_values:
                komitmen_total = sum(komitmen_values)
            
        # Calculate total % Achievement and Gap
        if komitmen_total is not None and komitmen_total != 0:
            # For percentage metrics (dpk_pct, npl_pct), totals['E'] is already a percentage
            # For other metrics, totals['E'] is in RUPIAH PENUH, need conversion to millions
            if metric_field in ['dpk_pct', 'npl_pct']:
                E_value = totals['E']  # Already a percentage
            else:
                E_value = totals['E'] / Decimal('1000000')  # Convert to millions
            
            # For DPK/NPL and %DPK/%NPL pages: Use reversed formula (Komitmen / E) Ã— 100
            if metric_field in ['dpk', 'npl', 'dpk_pct', 'npl_pct']:
                if E_value != 0:
                    komitmen_pct_ach_total = (komitmen_total / E_value) * Decimal('100')
                else:
                    komitmen_pct_ach_total = Decimal('110')  # IFERROR result
            else:
                # For OS and other metrics: Normal formula (E / Komitmen)
                komitmen_pct_ach_total = (E_value / komitmen_total) * Decimal('100')
                
            # Cap at 110%
            if komitmen_pct_ach_total > Decimal('110'):
                komitmen_pct_ach_total = Decimal('110')
            # Floor at 0%
            elif komitmen_pct_ach_total < Decimal('0'):
                komitmen_pct_ach_total = Decimal('0')
            # Gap thd Realisasi = E - Komitmen (both in same unit)
            komitmen_gab_real_total = E_value - komitmen_total
        else:
            # IFERROR: if komitmen is 0, return 110%
            komitmen_pct_ach_total = Decimal('110')
            if metric_field in ['dpk_pct', 'npl_pct']:
                E_value = totals['E']
            else:
                E_value = totals['E'] / Decimal('1000000')
            komitmen_gab_real_total = E_value
    
    totals['komitmen'] = komitmen_total
    totals['komitmen_pct_ach'] = komitmen_pct_ach_total
    totals['komitmen_gab_real'] = komitmen_gab_real_total
    
    return {
        'title': f'TOTAL {metric_field.upper()} {segment_filter} KANCA ONLY',
        'rows': rows,
        'totals': totals
    }


def build_kcp_only_table(date_columns, segment_filter='SMALL', metric_field='os', kol_adk_filter=None):
    """
    Build KCP ONLY table (only KCPs, sorted by parent KANCA).
    Groups KCP codes under their parent KANCA for better organization.
    
    Args:
        kol_adk_filter: Optional filter for kol_adk field (e.g., '2' for DPK)
    """
    rows = []
    
    # Get selected date for komitmen lookup (date E)
    selected_date = date_columns['E']['date']
    year = selected_date.year
    month = selected_date.month
    
    # Get komitmen data for the selected month (per uker)
    komitmen_segment, komitmen_metric = map_segment_and_metric_to_komitmen(segment_filter, metric_field)
    komitmen_data = None
    
    if komitmen_segment and komitmen_metric:
        # Check if komitmen exists for this month
        if check_komitmen_exists(year, month):
            komitmen_data = get_komitmen_for_month(year, month)  # Per uker data
    
    # Initialize totals
    totals = {
        'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0,
        'DtD': 0, 'MoM': 0, 'MtD': 0, 'YtD': 0,
        'DtD_pct': 0, 'MoM_pct': 0, 'MtD_pct': 0, 'YtD_pct': 0
    }
    
    # Get all KCP codes from UKER_MASTER, sorted by parent KANCA
    kcp_list = []
    for kode_kanca in KANCA_CODES:
        # Get KCP list for this KANCA using helper function
        kcp_data = get_kcp_by_kanca(kode_kanca)
        for kcp_code, kcp_name in kcp_data:
            kcp_list.append({
                'kode_kanca': kode_kanca,
                'kcp_code': kcp_code,
                'kcp_name': kcp_name,  # Store KCP name
                'kanca_name': KANCA_MASTER.get(kode_kanca, f"KANCA {kode_kanca}")
            })
    
    # Sort by parent KANCA code, then by KCP code (both are integers now)
    kcp_list.sort(key=lambda x: (x['kode_kanca'], x['kcp_code']))
    
    # Pre-fetch all metrics for all dates (optimization)
    # This avoids calling get_metric_by_uker() inside the loop
    metrics_by_date = {}
    for col_name, col_info in date_columns.items():
        metrics_by_date[col_name] = get_metric_by_uker(
            col_info['date'],
            segment_filter,
            metric_field,
            kol_adk_filter
        )
    
    # Build rows for each KCP
    for idx, kcp_info in enumerate(kcp_list, start=1):
        kcp_code = kcp_info['kcp_code']
        # Convert kcp_code to string because kode_uker in database is CharField
        kcp_code_str = str(kcp_code)
        
        # Get metrics for each date column from pre-fetched data
        A_val = metrics_by_date['A'].get(kcp_code_str, 0)
        B_val = metrics_by_date['B'].get(kcp_code_str, 0)
        C_val = metrics_by_date['C'].get(kcp_code_str, 0)
        D_val = metrics_by_date['D'].get(kcp_code_str, 0)
        E_val = metrics_by_date['E'].get(kcp_code_str, 0)
        
        # Calculate changes
        changes = calculate_changes(A_val, B_val, C_val, D_val, E_val)
        
        # Get komitmen value untuk KCP ini
        komitmen_value = None
        if komitmen_data and komitmen_segment and komitmen_metric:
            # SPECIAL CASE for %DPK/%NPL: Calculate komitmen as percentage
            if metric_field in ['dpk_pct', 'npl_pct']:
                # Get raw komitmen for numerator (DPK or NPL)
                komitmen_raw = get_komitmen_value(komitmen_data, kcp_code_str, komitmen_segment, komitmen_metric)
                # Get komitmen OS for denominator
                komitmen_os = get_komitmen_value(komitmen_data, kcp_code_str, komitmen_segment, 'os')
                
                # Calculate percentage: (DPK/NPL / OS) Ã— 100
                if komitmen_raw is not None and komitmen_os is not None and komitmen_os != 0:
                    komitmen_value = calculate_percentage_metric(komitmen_raw, komitmen_os)
                else:
                    komitmen_value = None
            else:
                # For other metrics: Use raw komitmen value
                komitmen_value = get_komitmen_value(komitmen_data, kcp_code_str, komitmen_segment, komitmen_metric)
        
        # Calculate komitmen % Achievement and Gap
        # Formula: =IFERROR(IF((E/Komitmen)>1.1,110%,IF((E/Komitmen)<0,0%,(E/Komitmen))),110%)
        # NOTE: E_val dari database dalam RUPIAH PENUH, komitmen dalam RIBUAN (juta rupiah)
        # SPECIAL CASE for DPK/NPL/DPK_PCT/NPL_PCT: Reversed formula (Komitmen / E) instead of (E / Komitmen)
        komitmen_pct_ach = None
        komitmen_gab_real = None
        if komitmen_value is not None and komitmen_value != 0:
            # For percentage metrics (dpk_pct, npl_pct), E_val is already a percentage
            # For other metrics, E_val is in RUPIAH PENUH, need conversion to millions
            if metric_field in ['dpk_pct', 'npl_pct']:
                E_value = E_val  # Already a percentage
            else:
                E_value = E_val / Decimal('1000000')  # Convert to millions
            
            # For DPK/NPL and %DPK/%NPL pages: Use reversed formula (Komitmen / E) Ã— 100
            if metric_field in ['dpk', 'npl', 'dpk_pct', 'npl_pct']:
                if E_value != 0:
                    ratio = komitmen_value / E_value  # REVERSED: Komitmen / E
                else:
                    ratio = Decimal('11')  # Will result in 110% cap
            else:
                # For OS and other metrics: Normal formula (E / Komitmen)
                ratio = E_value / komitmen_value
            
            if ratio > Decimal('1.1'):
                komitmen_pct_ach = Decimal('110')
            elif ratio < 0:
                komitmen_pct_ach = Decimal('0')
            else:
                komitmen_pct_ach = ratio * Decimal('100')
            
            # Gap = E - Komitmen (both in same unit)
            # Positive gap = surplus (realisasi > komitmen) â†’ hitam (for DPK/NPL reversed to red)
            # Negative gap = shortfall (realisasi < komitmen) â†’ merah (for DPK/NPL reversed to black)
            komitmen_gab_real = E_value - komitmen_value
        elif komitmen_value == 0 or komitmen_value is None:
            # IFERROR: jika error (pembagi nol), anggap 110%
            komitmen_pct_ach = Decimal('110')
            if metric_field in ['dpk_pct', 'npl_pct']:
                E_value = E_val
            else:
                E_value = E_val / Decimal('1000000')
            komitmen_gab_real = E_value  # Gap = realisasi (karena tidak ada target)
        
        # Build row
        row = {
            'no': idx,
            'kode_kanca': kcp_info['kode_kanca'],
            'kanca': f"{kcp_info['kanca_name']} - KCP {kcp_code}",
            'kode_uker': kcp_code,           # KCP code as kode_uker
            'uker': kcp_info['kcp_name'],    # KCP name as uker
            'A': A_val,
            'B': B_val,
            'C': C_val,
            'D': D_val,
            'E': E_val,
            'DtD': changes['DtD'],
            'DtD_pct': changes['DtD_pct'],
            'MoM': changes['MoM'],
            'MoM_pct': changes['MoM_pct'],
            'MtD': changes['MtD'],
            'MtD_pct': changes['MtD_pct'],
            'YtD': changes['YtD'],
            'YtD_pct': changes['YtD_pct'],
            # Komitmen value
            'komitmen': komitmen_value,
            'komitmen_pct_ach': komitmen_pct_ach,
            'komitmen_gab_real': komitmen_gab_real,
        }
        rows.append(row)
        
        # Add to totals
        totals['A'] += A_val
        totals['B'] += B_val
        totals['C'] += C_val
        totals['D'] += D_val
        totals['E'] += E_val
    
    # Calculate totals changes
    # For percentage metrics, recalculate from raw data instead of summing percentages
    if metric_field in ['dpk_pct', 'npl_pct']:
        # Determine which raw metrics to use
        if metric_field == 'dpk_pct':
            metric_raw = 'sml'
            base_raw = 'os'
            metric_filter = '2'   # DPK uses kol_adk='2'
            base_filter = None    # OS uses all kol_adk
        elif metric_field == 'npl_pct':
            metric_raw = 'npl'
            base_raw = 'os'
            metric_filter = None
            base_filter = None
        
        # Recalculate totals for each date from raw data
        totals_recalc = {}
        for col_name, col_info in date_columns.items():
            # Get metric sum (DPK or NPL) - only KCP codes
            metric_data = get_metric_by_uker(col_info['date'], segment_filter, metric_raw, metric_filter)
            metric_sum = sum(v for k, v in metric_data.items() if str(k) in [str(kcp) for kcp in KCP_CODES])
            
            # Get OS sum - only KCP codes, all kol_adk
            os_data = get_metric_by_uker(col_info['date'], segment_filter, base_raw, base_filter)
            os_sum = sum(v for k, v in os_data.items() if str(k) in [str(kcp) for kcp in KCP_CODES])
            
            # Calculate percentage
            totals_recalc[col_name] = calculate_percentage_metric(metric_sum, os_sum)
        
        # Replace totals with recalculated values
        totals['A'] = totals_recalc['A']
        totals['B'] = totals_recalc['B']
        totals['C'] = totals_recalc['C']
        totals['D'] = totals_recalc['D']
        totals['E'] = totals_recalc['E']
    
    totals_changes = calculate_changes(
        totals['A'], totals['B'], totals['C'], totals['D'], totals['E']
    )
    totals.update(totals_changes)
    
    # Calculate komitmen total
    komitmen_total = None
    komitmen_pct_ach_total = None
    komitmen_gab_real_total = None
    
    if komitmen_data:
        # SPECIAL CASE for %DPK/%NPL: Calculate komitmen total as percentage
        if metric_field in ['dpk_pct', 'npl_pct']:
            # Get all uker codes from rows (KCP codes only)
            # Convert to string because komitmen_dict keys are strings (kode_uker is CharField)
            uker_codes = [str(row['kode_uker']) for row in rows]
            
            # Sum raw komitmen for numerator (DPK or NPL)
            komitmen_raw_sum = Decimal('0')
            for kode_uker in uker_codes:
                komitmen_raw = get_komitmen_value(komitmen_data, kode_uker, komitmen_segment, komitmen_metric)
                if komitmen_raw:
                    komitmen_raw_sum += komitmen_raw
            
            # Sum komitmen OS for denominator
            komitmen_os_sum = Decimal('0')
            for kode_uker in uker_codes:
                komitmen_os = get_komitmen_value(komitmen_data, kode_uker, komitmen_segment, 'os')
                if komitmen_os:
                    komitmen_os_sum += komitmen_os
            
            # Calculate total percentage: (Total DPK/NPL / Total OS) Ã— 100
            if komitmen_os_sum != 0:
                komitmen_total = calculate_percentage_metric(komitmen_raw_sum, komitmen_os_sum)
            else:
                komitmen_total = None
        else:
            # For other metrics: Sum all komitmen values from rows
            komitmen_values = [row['komitmen'] for row in rows if row['komitmen'] is not None]
            if komitmen_values:
                komitmen_total = sum(komitmen_values)
            
        # Calculate total % Achievement and Gap
        if komitmen_total is not None and komitmen_total != 0:
            # For percentage metrics (dpk_pct, npl_pct), totals['E'] is already a percentage
            # For other metrics, totals['E'] is in RUPIAH PENUH, need conversion to millions
            if metric_field in ['dpk_pct', 'npl_pct']:
                E_value = totals['E']  # Already a percentage
            else:
                E_value = totals['E'] / Decimal('1000000')  # Convert to millions
            
            # For DPK/NPL and %DPK/%NPL pages: Use reversed formula (Komitmen / E) Ã— 100
            if metric_field in ['dpk', 'npl', 'dpk_pct', 'npl_pct']:
                if E_value != 0:
                    komitmen_pct_ach_total = (komitmen_total / E_value) * Decimal('100')
                else:
                    komitmen_pct_ach_total = Decimal('110')  # IFERROR result
            else:
                # For OS and other metrics: Normal formula (E / Komitmen)
                komitmen_pct_ach_total = (E_value / komitmen_total) * Decimal('100')
                
            # Cap at 110%
            if komitmen_pct_ach_total > Decimal('110'):
                komitmen_pct_ach_total = Decimal('110')
            # Floor at 0%
            elif komitmen_pct_ach_total < Decimal('0'):
                komitmen_pct_ach_total = Decimal('0')
            # Gap thd Realisasi = E - Komitmen (both in same unit)
            komitmen_gab_real_total = E_value - komitmen_total
        else:
            # IFERROR: if komitmen is 0, return 110%
            komitmen_pct_ach_total = Decimal('110')
            if metric_field in ['dpk_pct', 'npl_pct']:
                E_value = totals['E']
            else:
                E_value = totals['E'] / Decimal('1000000')
            komitmen_gab_real_total = E_value
    
    totals['komitmen'] = komitmen_total
    totals['komitmen_pct_ach'] = komitmen_pct_ach_total
    totals['komitmen_gab_real'] = komitmen_gab_real_total
    
    return {
        'title': f'TOTAL {metric_field.upper()} {segment_filter} KCP ONLY',
        'rows': rows,
        'totals': totals
    }


# ============================================================================
# Main Table Builder Function
# ============================================================================

def build_metric_tables(selected_date, segment_filter='SMALL', metric_field='os', kol_adk_filter=None):
    """
    Build all three tables (KONSOL, KANCA ONLY, KCP ONLY) for a specific metric.
    
    Args:
        selected_date: Date to analyze
        segment_filter: Segment to filter ('SMALL', 'MEDIUM', 'CC', 'KUR', 'SMALL NCC')
        metric_field: Metric to calculate ('os', 'dpk', 'npl', 'lar', 'sml', etc.)
        kol_adk_filter: Optional filter for kol_adk field (e.g., '2' for DPK)
    
    Returns:
        dict: Contains konsol, kanca, kcp tables and date_columns info
    """
    date_columns = get_date_columns(selected_date)
    
    return {
        'konsol': build_konsol_table(date_columns, segment_filter, metric_field, kol_adk_filter),
        'kanca': build_kanca_only_table(date_columns, segment_filter, metric_field, kol_adk_filter),
        'kcp': build_kcp_only_table(date_columns, segment_filter, metric_field, kol_adk_filter),
        'date_columns': date_columns,
    }


def build_summary_konsol_table(date_columns, kode_kanca_filter=None):
    """
    Build PERFORMANCE HIGHLIGHTS SME KONSOL summary table
    
    Contains all major segments and metrics in one comprehensive view:
    - END BAL - SME (OS)
    - BD KOL 2 - SME (Baki Debet Kolektibilitas 2)
    - % KOL 2 - SME (Percentage)
    - BD NPL - SME (Baki Debet NPL)
    - % NPL - SME (Percentage)
    - BD LR - SME (Baki Debet Lancar/Restructured)
    - % LR - SME (Percentage)
    - BD LAR - SME (Baki Debet LAR - Loans at Risk)
    - % LAR - SME (Percentage)
    - NASABAH - SME (Customer count)
    
    Args:
        date_columns: Dictionary containing date column definitions
        kode_kanca_filter: Optional KANCA code for filtering (None = RO BANDUNG/all)
    
    Returns:
        list: Rows containing all segment data with calculations
    """
    from dashboard.models import LW321
    from django.db.models import Sum, Count, Q
    from dashboard.formulas.komitmen_helper import get_komitmen_for_month, get_komitmen_value
    
    rows = []
    
    # Get komitmen data for the selected month
    komitmen_dict = get_komitmen_for_month(
        date_columns['E']['date'].year,
        date_columns['E']['date'].month
    )
    
    # Define segment structure
    segments_config = [
        {
            'title': 'END BAL - SME',
            'metric': 'os',
            'segments': [
                ('Medium', 'MEDIUM', None),
                ('Small + KUR', ['SMALL', 'SMALL NCC', 'KUR', 'CC'], None),
                ('Small', ['SMALL', 'SMALL NCC', 'CC'], None),
                ('- Small Non CC', 'SMALL NCC', None),
                ('- CC', 'CC', None),
                ('KUR', 'KUR', None),
            ]
        },
        {
            'title': 'BD KOL 2 - SME',
            'metric': 'kol2',  # Changed from 'os' to differentiate
            'kol_filter': '2',
            'segments': [
                ('Medium', 'MEDIUM', '2'),
                ('Small + KUR', ['SMALL', 'SMALL NCC', 'KUR', 'CC'], '2'),
                ('Small', ['SMALL', 'SMALL NCC', 'CC'], '2'),
                ('- Small Non CC', 'SMALL NCC', '2'),
                ('- CC', 'CC', '2'),
                ('KUR', 'KUR', '2'),
            ]
        },
        {
            'title': '% KOL 2 - SME',
            'metric': 'kol2_pct',
            'segments': [
                ('Medium', 'MEDIUM', None),
                ('Small + KUR', ['SMALL', 'SMALL NCC', 'KUR', 'CC'], None),
                ('Small', ['SMALL', 'SMALL NCC', 'CC'], None),
                ('- Small Non CC', 'SMALL NCC', None),
                ('- CC', 'CC', None),
                ('KUR', 'KUR', None),
            ]
        },
        {
            'title': 'BD NPL - SME',
            'metric': 'npl',  # Changed from 'os' to differentiate
            'kol_filter': ['3', '4', '5'],
            'segments': [
                ('Medium', 'MEDIUM', ['3', '4', '5']),
                ('Small + KUR', ['SMALL', 'SMALL NCC', 'KUR', 'CC'], ['3', '4', '5']),
                ('Small', ['SMALL', 'SMALL NCC', 'CC'], ['3', '4', '5']),
                ('- Small Non CC', 'SMALL NCC', ['3', '4', '5']),
                ('- CC', 'CC', ['3', '4', '5']),
                ('KUR', 'KUR', ['3', '4', '5']),
            ]
        },
        {
            'title': '% NPL - SME',
            'metric': 'npl_pct',
            'segments': [
                ('Medium', 'MEDIUM', None),
                ('Small + KUR', ['SMALL', 'SMALL NCC', 'KUR', 'CC'], None),
                ('Small', ['SMALL', 'SMALL NCC', 'CC'], None),
                ('- Small Non CC', 'SMALL NCC', None),
                ('- CC', 'CC', None),
                ('KUR', 'KUR', None),
            ]
        },
        {
            'title': 'BD LR - SME',
            'metric': 'lr',  # Changed from 'os' to differentiate
            'kol_filter': '1',
            'flag_restruk': 'Y',
            'segments': [
                ('Medium', 'MEDIUM', '1'),
                ('Small + KUR', ['SMALL', 'SMALL NCC', 'KUR', 'CC'], '1'),
                ('Small', ['SMALL', 'SMALL NCC', 'CC'], '1'),
                ('- Small Non CC', 'SMALL NCC', '1'),
                ('- CC', 'CC', '1'),
                ('KUR', 'KUR', '1'),
            ]
        },
        {
            'title': '% LR - SME',
            'metric': 'lr_pct',
            'segments': [
                ('Medium', 'MEDIUM', None),
                ('Small + KUR', ['SMALL', 'SMALL NCC', 'KUR', 'CC'], None),
                ('Small', ['SMALL', 'SMALL NCC', 'CC'], None),
                ('KUR', 'KUR', None),
            ]
        },
        {
            'title': 'BD LAR - SME',
            'metric': 'lar',  # Special metric that calculates SML + NPL + LR
            'segments': [
                ('Medium', 'MEDIUM', None),
                ('Small + KUR', ['SMALL', 'SMALL NCC', 'KUR', 'CC'], None),
                ('Small', ['SMALL', 'SMALL NCC', 'CC'], None),
                ('- Small Non CC', 'SMALL NCC', None),
                ('- CC', 'CC', None),
                ('KUR', 'KUR', None),
            ]
        },
        {
            'title': '% LAR - SME',
            'metric': 'lar_pct',
            'segments': [
                ('Medium', 'MEDIUM', None),
                ('Small + KUR', ['SMALL', 'SMALL NCC', 'KUR', 'CC'], None),
                ('Small', ['SMALL', 'SMALL NCC', 'CC'], None),
                ('KUR', 'KUR', None),
            ]
        },
        {
            'title': 'NASABAH - SME',
            'metric': 'nasabah',
            'segments': [
                ('Medium', 'MEDIUM', None),
                ('Small + KUR', ['SMALL', 'SMALL NCC', 'KUR', 'CC'], None),
                ('Small', ['SMALL', 'SMALL NCC', 'CC'], None),
                ('- Small Non CC', 'SMALL NCC', None),
                ('- CC', 'CC', None),
                ('KUR', 'KUR', None),
            ]
        },
    ]
    
    def get_data_for_segment(date, segment_filter, kol_filter=None, metric='os', flag_restruk_filter=None):
        """Get data for a specific segment and date"""
        from dashboard.formulas.segmentation import get_segment_annotation
        from dashboard.formulas.uker_mapping import UKER_MASTER, KANCA_CODES
        from django.db.models import Q
        
        periode_str = date.strftime("%d/%m/%Y")
        qs = LW321.objects.filter(periode=periode_str)
        
        # Add segment annotation
        qs = qs.annotate(segment=get_segment_annotation())
        
        # Apply kanca filter if specified
        if kode_kanca_filter:
            # Get all uker codes that belong to this kanca
            uker_codes_for_kanca = []
            
            # Check if this kode_kanca is a KANCA itself
            if kode_kanca_filter in KANCA_CODES:
                uker_codes_for_kanca.append(str(kode_kanca_filter))
            
            # Get all KCP under this KANCA
            for kode_uker, (nama_uker, kode_kanca_induk) in UKER_MASTER.items():
                if kode_kanca_induk == kode_kanca_filter:
                    uker_codes_for_kanca.append(str(kode_uker))
            
            # Filter by kode_uker
            if uker_codes_for_kanca:
                qs = qs.filter(kode_uker__in=uker_codes_for_kanca)
        
        # Apply segment filter
        if isinstance(segment_filter, list):
            qs = qs.filter(segment__in=segment_filter)
        else:
            qs = qs.filter(segment=segment_filter)
        
        # Apply kol filter if specified (using kol_adk field)
        if kol_filter:
            if isinstance(kol_filter, list):
                qs = qs.filter(kol_adk__in=kol_filter)
            else:
                qs = qs.filter(kol_adk=kol_filter)
        
        # Apply flag_restruk filter for LR metric
        if flag_restruk_filter:
            qs = qs.filter(flag_restruk=flag_restruk_filter)
        
        # Get the appropriate metric
        if metric == 'nasabah':
            # Sum nasabah field WHERE dub_nasabah='TRUE'
            qs = qs.filter(Q(dub_nasabah__iexact='TRUE'))
            result = qs.aggregate(total=Sum('nasabah'))
            return float(result['total'] or 0)
        elif metric == 'lar':
            # LAR = SML + NPL + LR
            # SML = kol_adk='2'
            # NPL = kol_adk IN ('3', '4', '5')
            # LR = kol_adk='1' AND flag_restruk='Y'
            sml = get_data_for_segment(date, segment_filter, kol_filter='2', metric='os')
            npl = get_data_for_segment(date, segment_filter, kol_filter=['3', '4', '5'], metric='os')
            lr = get_data_for_segment(date, segment_filter, kol_filter='1', metric='os', flag_restruk_filter='Y')
            return sml + npl + lr
        elif metric in ['kol2', 'npl', 'lr']:
            # These are absolute metrics but use OS aggregation
            # Just treat them as 'os' for data retrieval
            result = qs.aggregate(total=Sum('os'))
            value = float(result['total'] or 0)
            # Convert from rupiah penuh to millions
            return value / 1_000_000
        else:
            result = qs.aggregate(total=Sum('os'))
            value = float(result['total'] or 0)
            # Convert from rupiah penuh to millions
            return value / 1_000_000
    
    def get_percentage_metric(date, segment_filter, numerator_kol, metric_type):
        """Calculate percentage metrics (KOL2%, NPL%, LR%, LAR%)"""
        # Get denominator (total OS without kol filter)
        denominator = get_data_for_segment(date, segment_filter, kol_filter=None, metric='os')
        
        if denominator == 0:
            return 0
        
        # Get numerator based on metric type
        if metric_type == 'kol2_pct':
            numerator = get_data_for_segment(date, segment_filter, kol_filter='2', metric='os')
        elif metric_type == 'npl_pct':
            numerator = get_data_for_segment(date, segment_filter, kol_filter=['3', '4', '5'], metric='os')
        elif metric_type == 'lr_pct':
            # LR = kol_adk='1' AND flag_restruk='Y'
            numerator = get_data_for_segment(date, segment_filter, kol_filter='1', metric='os', flag_restruk_filter='Y')
        elif metric_type == 'lar_pct':
            # LAR = SML + NPL + LR = kol_adk IN ('2', '3', '4', '5') OR (kol_adk='1' AND flag_restruk='Y')
            sml = get_data_for_segment(date, segment_filter, kol_filter='2', metric='os')
            npl = get_data_for_segment(date, segment_filter, kol_filter=['3', '4', '5'], metric='os')
            lr = get_data_for_segment(date, segment_filter, kol_filter='1', metric='os', flag_restruk_filter='Y')
            numerator = sml + npl + lr
        else:
            numerator = 0
        
        return (numerator / denominator) * 100
    
    # Build rows for each segment group
    for config in segments_config:
        # Initialize totals for this group (Medium + Small + KUR only)
        totals = {
            'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0,
            'komitmen': 0
        }
        
        # First pass: collect data and calculate totals from Medium, Small, KUR
        segment_data = []
        
        segment_data = []
        
        # Add data rows for each segment
        for segment_name, segment_filter, kol_filter in config['segments']:
            metric = config['metric']
            flag_restruk = config.get('flag_restruk', None)  # Get flag_restruk from config if exists
            
            # Get data for all date columns
            if metric in ['kol2_pct', 'npl_pct', 'lr_pct', 'lar_pct']:
                # Percentage metrics
                val_a = get_percentage_metric(date_columns['A']['date'], segment_filter, kol_filter, metric)
                val_b = get_percentage_metric(date_columns['B']['date'], segment_filter, kol_filter, metric)
                val_c = get_percentage_metric(date_columns['C']['date'], segment_filter, kol_filter, metric)
                val_d = get_percentage_metric(date_columns['D']['date'], segment_filter, kol_filter, metric)
                val_e = get_percentage_metric(date_columns['E']['date'], segment_filter, kol_filter, metric)
            elif metric == 'lar':
                # LAR metric (no flag_restruk needed, handled inside get_data_for_segment)
                val_a = get_data_for_segment(date_columns['A']['date'], segment_filter, None, metric)
                val_b = get_data_for_segment(date_columns['B']['date'], segment_filter, None, metric)
                val_c = get_data_for_segment(date_columns['C']['date'], segment_filter, None, metric)
                val_d = get_data_for_segment(date_columns['D']['date'], segment_filter, None, metric)
                val_e = get_data_for_segment(date_columns['E']['date'], segment_filter, None, metric)
            else:
                # Absolute metrics (OS, Nasabah, or LR)
                val_a = get_data_for_segment(date_columns['A']['date'], segment_filter, kol_filter, metric, flag_restruk)
                val_b = get_data_for_segment(date_columns['B']['date'], segment_filter, kol_filter, metric, flag_restruk)
                val_c = get_data_for_segment(date_columns['C']['date'], segment_filter, kol_filter, metric, flag_restruk)
                val_d = get_data_for_segment(date_columns['D']['date'], segment_filter, kol_filter, metric, flag_restruk)
                val_e = get_data_for_segment(date_columns['E']['date'], segment_filter, kol_filter, metric, flag_restruk)
            
            # Calculate growth metrics
            dtd = val_e - val_d
            dtd_pct = (dtd / val_d * 100) if val_d else 0
            
            mom = val_e - val_b
            mom_pct = (mom / val_b * 100) if val_b else 0
            
            mtd = val_e - val_c
            mtd_pct = (mtd / val_c * 100) if val_c else 0
            
            ytd = val_e - val_a
            ytd_pct = (ytd / val_a * 100) if val_a else 0
            
            # Get komitmen data
            # Map segment to komitmen metric
            komitmen_metric_map = {
                'os': 'os',
                'kol2_pct': 'kol2_pct',
                'npl_pct': 'npl_pct',
                'lr_pct': 'lr_pct',
                'lar_pct': 'lar_pct',
                'nasabah': 'nasabah',
            }
            
            komitmen_metric = komitmen_metric_map.get(metric, 'os')
            
            # Get komitmen identifier
            if kode_kanca_filter:
                komitmen_identifier = str(kode_kanca_filter)
            else:
                komitmen_identifier = 'RO_BANDUNG'
            
            # Get komitmen value
            if metric in ['kol2_pct', 'npl_pct', 'lr_pct', 'lar_pct']:
                # For percentage metrics, calculate from raw values
                komitmen_raw = get_komitmen_value(
                    komitmen_dict,
                    komitmen_identifier,
                    segment_filter if not isinstance(segment_filter, list) else segment_filter[0],
                    komitmen_metric.replace('_pct', '')
                )
                komitmen_os = get_komitmen_value(
                    komitmen_dict,
                    komitmen_identifier,
                    segment_filter if not isinstance(segment_filter, list) else segment_filter[0],
                    'os'
                )
                komitmen_value = calculate_percentage_metric(komitmen_raw, komitmen_os)
            else:
                komitmen_value = get_komitmen_value(
                    komitmen_dict,
                    komitmen_identifier,
                    segment_filter if not isinstance(segment_filter, list) else segment_filter[0],
                    komitmen_metric
                )
            
            # Handle None komitmen value
            if komitmen_value is None:
                komitmen_value = 0
            
            # Calculate komitmen % achievement and gap
            if metric in ['kol2_pct', 'npl_pct', 'lr_pct', 'lar_pct']:
                # For percentage metrics, use reversed formula
                komitmen_pct_ach = (komitmen_value / val_e * 100) if val_e else 0
            else:
                # For absolute metrics, use normal formula
                komitmen_pct_ach = (val_e / komitmen_value * 100) if komitmen_value else 0
            
            komitmen_gab_real = val_e - komitmen_value
            
            row = {
                'is_header': False,
                'is_total': False,
                'segment': segment_name,
                'metric_type': metric,
                'A': val_a,
                'B': val_b,
                'C': val_c,
                'D': val_d,
                'E': val_e,
                'DtD': dtd,
                'DtD_pct': dtd_pct,
                'MoM': mom,
                'MoM_pct': mom_pct,
                'MtD': mtd,
                'MtD_pct': mtd_pct,
                'YtD': ytd,
                'YtD_pct': ytd_pct,
                'komitmen': komitmen_value,
                'komitmen_pct_ach': komitmen_pct_ach,
                'komitmen_gab_real': komitmen_gab_real,
            }
            
            segment_data.append(row)
            
            # Accumulate totals only for Medium, Small (aggregate), and KUR
            # These are the 3 main rows that will be summed for total
            if segment_name in ['Medium', 'Small', 'KUR']:
                if metric not in ['kol2_pct', 'npl_pct', 'lr_pct', 'lar_pct']:
                    totals['A'] += val_a
                    totals['B'] += val_b
                    totals['C'] += val_c
                    totals['D'] += val_d
                    totals['E'] += val_e
                    totals['komitmen'] += komitmen_value
        
        # Calculate totals growth from Medium + Small (aggregate) + KUR
        total_dtd = totals['E'] - totals['D']
        total_dtd_pct = (total_dtd / totals['D'] * 100) if totals['D'] else 0
        
        total_mom = totals['E'] - totals['B']
        total_mom_pct = (total_mom / totals['B'] * 100) if totals['B'] else 0
        
        total_mtd = totals['E'] - totals['C']
        total_mtd_pct = (total_mtd / totals['C'] * 100) if totals['C'] else 0
        
        total_ytd = totals['E'] - totals['A']
        total_ytd_pct = (total_ytd / totals['A'] * 100) if totals['A'] else 0
        
        total_komitmen_pct_ach = (totals['E'] / totals['komitmen'] * 100) if totals['komitmen'] else 0
        total_komitmen_gap = totals['E'] - totals['komitmen']
        
        # For percentage metrics, calculate totals differently
        if config['metric'] in ['kol2_pct', 'npl_pct', 'lr_pct', 'lar_pct']:
            # Recalculate percentage from Medium + Small (all small segments) + KUR
            all_segments = ['MEDIUM', 'SMALL', 'SMALL NCC', 'CC', 'KUR']
            kol_f = config.get('kol_filter')
            
            total_a = get_percentage_metric(date_columns['A']['date'], all_segments, kol_f, config['metric'])
            total_b = get_percentage_metric(date_columns['B']['date'], all_segments, kol_f, config['metric'])
            total_c = get_percentage_metric(date_columns['C']['date'], all_segments, kol_f, config['metric'])
            total_d = get_percentage_metric(date_columns['D']['date'], all_segments, kol_f, config['metric'])
            total_e = get_percentage_metric(date_columns['E']['date'], all_segments, kol_f, config['metric'])
            
            # Create header row as total row for percentage metrics
            header_row = {
                'is_header': False,
                'is_total': True,
                'segment': config['title'],
                'metric_type': config['metric'],
                'A': total_a,
                'B': total_b,
                'C': total_c,
                'D': total_d,
                'E': total_e,
                'DtD': total_e - total_d,
                'DtD_pct': ((total_e - total_d) / total_d * 100) if total_d else 0,
                'MoM': total_e - total_b,
                'MoM_pct': ((total_e - total_b) / total_b * 100) if total_b else 0,
                'MtD': total_e - total_c,
                'MtD_pct': ((total_e - total_c) / total_c * 100) if total_c else 0,
                'YtD': total_e - total_a,
                'YtD_pct': ((total_e - total_a) / total_a * 100) if total_a else 0,
                'komitmen': 0,
                'komitmen_pct_ach': 0,
                'komitmen_gab_real': 0,
            }
        else:
            # Create header row as total row for absolute metrics
            header_row = {
                'is_header': False,
                'is_total': True,
                'segment': config['title'],
                'metric_type': config['metric'],
                'A': totals['A'],
                'B': totals['B'],
                'C': totals['C'],
                'D': totals['D'],
                'E': totals['E'],
                'DtD': total_dtd,
                'DtD_pct': total_dtd_pct,
                'MoM': total_mom,
                'MoM_pct': total_mom_pct,
                'MtD': total_mtd,
                'MtD_pct': total_mtd_pct,
                'YtD': total_ytd,
                'YtD_pct': total_ytd_pct,
                'komitmen': totals['komitmen'],
                'komitmen_pct_ach': total_komitmen_pct_ach,
                'komitmen_gab_real': total_komitmen_gap,
            }
        
        # Add header row first (which contains totals)
        rows.append(header_row)
        
        # Then add all segment detail rows
        rows.extend(segment_data)
    
    return rows

