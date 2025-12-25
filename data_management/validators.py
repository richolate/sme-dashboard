"""
Validators untuk upload komitmen data - Index-Based Reading
"""
import pandas as pd
import re
from datetime import datetime
from dashboard.models import LW321
from dashboard.formulas.uker_mapping import UKER_MASTER


# Daftar kode uker yang sudah ditutup (skip saat upload)
CLOSED_UKER_CODES = {'1077', '1108', '1337', '1345', '2162', '2202', '2000', '2103'}


def extract_period_from_filename(filename):
    """
    Extract periode from filename patterns:
    - KOMITMEN_NOV_2025.xlsx → 2025-11-01
    - KOMITMEN_NOVEMBER_2025.xlsx → 2025-11-01
    - KOMITMEN_11_2025.xlsx → 2025-11-01
    
    Returns: datetime.date object or None
    """
    month_map = {
        'jan': 1, 'january': 1, 'januari': 1,
        'feb': 2, 'february': 2, 'februari': 2,
        'mar': 3, 'march': 3, 'maret': 3,
        'apr': 4, 'april': 4,
        'may': 5, 'mei': 5,
        'jun': 6, 'june': 6, 'juni': 6,
        'jul': 7, 'july': 7, 'juli': 7,
        'aug': 8, 'august': 8, 'agustus': 8,
        'sep': 9, 'september': 9,
        'oct': 10, 'october': 10, 'oktober': 10,
        'nov': 11, 'november': 11,
        'dec': 12, 'december': 12, 'desember': 12
    }
    
    # Pattern 1: KOMITMEN_NOV_2025.xlsx atau KOMITMEN_NOVEMBER_2025.xlsx
    pattern1 = r'[_\-\s]([a-z]+)[_\-\s](\d{4})'
    if match := re.search(pattern1, filename.lower()):
        month_str, year = match.groups()
        if month := month_map.get(month_str):
            return datetime(int(year), month, 1).date()
    
    # Pattern 2: KOMITMEN_11_2025.xlsx
    pattern2 = r'[_\-\s](\d{1,2})[_\-\s](\d{4})'
    if match := re.search(pattern2, filename):
        month, year = match.groups()
        month_int = int(month)
        if 1 <= month_int <= 12:
            return datetime(int(year), month_int, 1).date()
    
    return None


def clean_numeric_value(value):
    """
    Convert Excel value to Decimal
    - Angka → Decimal
    - "-" → None
    - Kosong/NaN → None
    - String angka → Decimal
    """
    if pd.isna(value):
        return None
    if isinstance(value, str):
        value = value.strip()
        if value == '' or value == '-':
            return None
        # Remove common formatting
        value = value.replace(',', '').replace(' ', '')
        try:
            return float(value)
        except ValueError:
            return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


# Column mapping berdasarkan INDEX (0-based)
# Format Excel: A=0, B=1, C=2, D=3, E=4, F=5, ...
COLUMN_INDICES = {
    'kode_kanca': 0,      # Column A
    'kode_uker': 1,       # Column B
    'nama_kanca': 2,      # Column C
    'nama_uker': 3,       # Column D
    
    # KUR RITEL (E-I)
    'kur_deb': 4,         # Column E
    'kur_os': 5,          # Column F
    'kur_pl': 6,          # Column G
    'kur_npl': 7,         # Column H
    'kur_dpk': 8,         # Column I
    
    # SMALL SD 5M (J-N)
    'small_deb': 9,       # Column J
    'small_os': 10,       # Column K
    'small_pl': 11,       # Column L
    'small_npl': 12,      # Column M
    'small_dpk': 13,      # Column N
    
    # KECIL NCC (O-S)
    'kecil_ncc_deb': 14,  # Column O
    'kecil_ncc_os': 15,   # Column P
    'kecil_ncc_pl': 16,   # Column Q
    'kecil_ncc_npl': 17,  # Column R
    'kecil_ncc_dpk': 18,  # Column S
    
    # KECIL CC (T-X)
    'kecil_cc_deb': 19,   # Column T
    'kecil_cc_os': 20,    # Column U
    'kecil_cc_pl': 21,    # Column V
    'kecil_cc_npl': 22,   # Column W
    'kecil_cc_dpk': 23,   # Column X
}


def validate_komitmen_excel(file_path, expected_periode=None):
    """
    Validate Excel structure and data using INDEX-BASED reading
    Data dimulai dari baris 3 (index 2) sampai ketemu "RO" atau "Region"
    
    Returns: dict dengan keys:
    - valid: bool
    - errors: list of error messages
    - warnings: list of warning messages
    - data_row_count: int
    - total_row_count: int
    - total_rows: list of dict (for display)
    - periode: datetime.date (extracted from filename)
    - data_df: pandas.DataFrame (clean data without total rows)
    """
    try:
        # Read Excel tanpa header, mulai dari baris 3 (index 2)
        df = pd.read_excel(file_path, header=None, skiprows=2)
    except Exception as e:
        return {
            'valid': False,
            'errors': [f"❌ Gagal membaca file Excel: {str(e)}"],
            'warnings': [],
            'data_row_count': 0,
            'total_row_count': 0,
            'total_rows': [],
            'periode': None,
            'data_df': None
        }
    
    errors = []
    warnings = []
    
    # 1. Check minimum columns (24 kolom: A-X)
    min_cols = 24  # A=0 sampai X=23, jadi butuh 24 kolom
    if len(df.columns) < min_cols:
        errors.append(f"❌ Jumlah kolom tidak cukup. Dibutuhkan minimal {min_cols} kolom (A-X), ditemukan {len(df.columns)}")
        return {
            'valid': False,
            'errors': errors,
            'warnings': warnings,
            'data_row_count': 0,
            'total_row_count': 0,
            'total_rows': [],
            'periode': None,
            'data_df': None,
            'preview_rows': []
        }
    
    # 2. Extract periode from filename
    import os
    filename = os.path.basename(file_path)
    periode = extract_period_from_filename(filename)
    
    if not periode:
        errors.append(f"❌ Tidak dapat mengekstrak periode dari nama file: {filename}. Gunakan format: KOMITMEN_NOV_2025.xlsx")
    
    if expected_periode and periode and periode != expected_periode:
        warnings.append(f"⚠️ Periode dari filename ({periode}) berbeda dengan expected ({expected_periode})")
    
    # 3. Separate data rows from total rows
    # Total rows contain "Region" or "RO" (as whole words) in column D (index 3 = Uker)
    # Use word boundary \b to avoid matching "Patrol" or "METRO"
    df[3] = df[3].astype(str)
    total_mask = df[3].str.contains(r'\b(Region|RO)\b', case=False, na=False, regex=True)
    total_rows = df[total_mask]
    data_rows = df[~total_mask]
    
    # Remove completely empty rows (where Kode Uker is empty)
    data_rows = data_rows.dropna(subset=[COLUMN_INDICES['kode_uker']], how='all')
    
    if len(data_rows) == 0:
        errors.append("❌ Tidak ada data yang valid ditemukan")
        return {
            'valid': False,
            'errors': errors,
            'warnings': warnings,
            'data_row_count': 0,
            'total_row_count': len(total_rows),
            'total_rows': [],
            'periode': periode,
            'data_df': None,
            'preview_rows': []
        }
    
    # 4. Validate totals (for user verification)
    if not total_rows.empty:
        # Check sample columns (KUR OS, SMALL OS)
        sample_checks = [
            ('KUR RITEL OS', COLUMN_INDICES['kur_os']),
            ('SMALL SD 5M DEB', COLUMN_INDICES['small_deb']),
        ]
        
        for col_name, col_idx in sample_checks:
            try:
                data_values = data_rows[col_idx].apply(clean_numeric_value)
                total_values = total_rows[col_idx].apply(clean_numeric_value)
                
                calculated_total = data_values.sum()
                declared_total = total_values.iloc[0] if len(total_values) > 0 else 0
                
                if declared_total and calculated_total and declared_total != 0:
                    diff = abs(calculated_total - declared_total)
                    diff_pct = (diff / declared_total * 100) if declared_total else 0
                    
                    if diff_pct > 1:  # Tolerance 1%
                        warnings.append(
                            f"⚠️ Total tidak cocok untuk {col_name}: "
                            f"Calculated={calculated_total:,.0f}, "
                            f"Declared={declared_total:,.0f}, "
                            f"Selisih={diff:,.0f} ({diff_pct:.1f}%)"
                        )
            except Exception as e:
                warnings.append(f"⚠️ Tidak dapat validasi total untuk {col_name}: {str(e)}")
    
    # 5. Filter closed uker codes
    # Clean and standardize kode_uker format FIRST
    data_rows[COLUMN_INDICES['kode_uker']] = (
        data_rows[COLUMN_INDICES['kode_uker']]
        .astype(str)
        .str.strip()
        .str.replace('.0', '', regex=False)  # Remove .0 dari float
        .str.replace(',', '', regex=False)   # Remove komma
    )
    
    # Check for closed uker codes in file
    file_ukers_series = data_rows[COLUMN_INDICES['kode_uker']]
    closed_ukers_in_file = file_ukers_series[file_ukers_series.isin(CLOSED_UKER_CODES)].unique()
    
    if len(closed_ukers_in_file) > 0:
        warnings.append(
            f"⚠️ {len(closed_ukers_in_file)} Kode Uker sudah ditutup dan akan di-skip: "
            f"{', '.join(sorted(closed_ukers_in_file))}"
        )
        warnings.append(f"   Data untuk uker ini tidak akan di-upload")
    
    # Remove closed uker codes from data
    initial_row_count = len(data_rows)
    data_rows = data_rows[~file_ukers_series.isin(CLOSED_UKER_CODES)]
    removed_count = initial_row_count - len(data_rows)
    
    if removed_count > 0:
        warnings.append(f"   {removed_count} baris data di-skip karena uker sudah ditutup")
    
    # Check if no data left after filtering
    if len(data_rows) == 0:
        errors.append("❌ Tidak ada data yang valid setelah filter uker yang ditutup")
        return {
            'valid': False,
            'errors': errors,
            'warnings': warnings,
            'data_row_count': 0,
            'total_row_count': len(total_rows),
            'total_rows': [],
            'periode': periode,
            'data_df': None,
            'preview_rows': []
        }
    
    # 6. Check kode_uker exists in system (UKER_MASTER)
    # Use UKER_MASTER as the source of truth for valid uker codes
    valid_ukers = set(str(k) for k in UKER_MASTER.keys())
    
    # Get unique kode_uker from file (already cleaned in step 5)
    file_ukers = set(data_rows[COLUMN_INDICES['kode_uker']].unique())
    
    invalid_ukers = file_ukers - valid_ukers
    
    if invalid_ukers:
        invalid_list = sorted(list(invalid_ukers))[:10]  # Show first 10
        warnings.append(
            f"⚠️ {len(invalid_ukers)} Kode Uker tidak ditemukan di UKER_MASTER: "
            f"{', '.join(invalid_list)}"
            f"{' ...' if len(invalid_ukers) > 10 else ''}"
        )
        warnings.append(f"   Data untuk uker ini akan tetap di-upload")
    
    # Additional check: which ukers are not in LW321 database (informational only)
    existing_ukers_in_lw321 = set(LW321.objects.values_list('kode_uker', flat=True).distinct())
    ukers_not_in_lw321 = file_ukers - existing_ukers_in_lw321
    
    if ukers_not_in_lw321:
        ukers_list = sorted(list(ukers_not_in_lw321))[:5]
        warnings.append(
            f"ℹ️ {len(ukers_not_in_lw321)} Kode Uker belum ada di LW321 database: "
            f"{', '.join(ukers_list)}"
            f"{' ...' if len(ukers_not_in_lw321) > 5 else ''}"
        )
        warnings.append(f"   Data akan di-upload tapi mungkin belum muncul di dashboard sampai LW321 di-update")
    
    # 7. Check duplicates
    dupes = data_rows[data_rows.duplicated([COLUMN_INDICES['kode_uker']], keep=False)]
    if len(dupes) > 0:
        dupe_ukers = dupes[COLUMN_INDICES['kode_uker']].unique().tolist()[:5]
        errors.append(f"❌ Kode Uker duplikat ditemukan: {', '.join(map(str, dupe_ukers))}")
    
    # 8. Summary - prepare total rows for display
    total_rows_list = []
    if not total_rows.empty:
        for _, row in total_rows.iterrows():
            total_rows_list.append({
                'uker': str(row[COLUMN_INDICES['nama_uker']]),
                'kur_os': clean_numeric_value(row[COLUMN_INDICES['kur_os']]),
                'small_os': clean_numeric_value(row[COLUMN_INDICES['small_os']]),
                'kecil_ncc_os': clean_numeric_value(row[COLUMN_INDICES['kecil_ncc_os']]),
                'kecil_cc_os': clean_numeric_value(row[COLUMN_INDICES['kecil_cc_os']]),
            })
    
    # 9. Prepare preview rows (first 10 data rows)
    preview_rows_list = []
    for _, row in data_rows.head(10).iterrows():
        preview_rows_list.append({
            'kode_kanca': str(row[COLUMN_INDICES['kode_kanca']]).strip(),
            'kode_uker': str(row[COLUMN_INDICES['kode_uker']]).strip(),
            'nama_kanca': str(row[COLUMN_INDICES['nama_kanca']]).strip(),
            'nama_uker': str(row[COLUMN_INDICES['nama_uker']]).strip(),
            'kur_os': clean_numeric_value(row[COLUMN_INDICES['kur_os']]),
            'small_os': clean_numeric_value(row[COLUMN_INDICES['small_os']]),
            'kecil_ncc_os': clean_numeric_value(row[COLUMN_INDICES['kecil_ncc_os']]),
            'kecil_cc_os': clean_numeric_value(row[COLUMN_INDICES['kecil_cc_os']]),
        })
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'data_row_count': len(data_rows),
        'total_row_count': len(total_rows),
        'total_rows': total_rows_list,
        'periode': periode,
        'data_df': data_rows if len(errors) == 0 else None,
        'preview_rows': preview_rows_list
    }
