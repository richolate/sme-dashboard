import pandas as pd
from decimal import Decimal, InvalidOperation
from dashboard.models import LW321

COLUMN_FIELD_MAP = {
    'PERIODE': 'periode',
    'KANCA': 'kanca',
    'KODE UKER': 'kode_uker',
    'UKER': 'uker',
    'LN TYPE': 'ln_type',
    'NOMOR REKENING': 'nomor_rekening',
    'NAMA DEBITUR': 'nama_debitur',
    'PLAFON': 'plafon',
    'NEXT PMT DATE': 'next_pmt_date',
    'NEXT INT PMT DATE': 'next_int_pmt_date',
    'RATE': 'rate',
    'TGL MENUNGGAK': 'tgl_menunggak',
    'TGL REALISASI': 'tgl_realisasi',
    'TGL JATUH TEMPO': 'tgl_jatuh_tempo',
    'JANGKA WAKTU': 'jangka_waktu',
    'FLAG RESTRUK': 'flag_restruk',
    'CIFNO': 'cif_no',
    'KOLEKTIBILITAS LANCAR': 'kolektibilitas_lancar',
    'KOLEKTIBILITAS DPK': 'kolektibilitas_dpk',
    'KOLEKTIBILITAS KURANG LANCAR': 'kolektibilitas_kurang_lancar',
    'KOLEKTIBILITAS DIRAGUKAN': 'kolektibilitas_diragukan',
    'KOLEKTIBILITAS MACET': 'kolektibilitas_macet',
    'TUNGGAKAN POKOK': 'tunggakan_pokok',
    'TUNGGAKAN BUNGA': 'tunggakan_bunga',
    'TUNGGAKAN PINALTI': 'tunggakan_pinalti',
    'CODE': 'code',
    'DESCRIPTION': 'description',
    'KOL_ADK': 'kol_adk',
    'PN RM': 'pn_rm',
    'NAMA RM': 'nama_rm',
    'OS': 'os',
    'NASABAH': 'nasabah',
    'DUB NASABAH': 'dub_nasabah',
}

DATE_STRING_FIELDS = {
    'next_pmt_date', 'next_int_pmt_date', 'tgl_menunggak',
    'tgl_realisasi', 'tgl_jatuh_tempo',
}

PERIODE_FIELD = 'periode'

DECIMAL_FIELDS = {
    'plafon', 'rate', 'tunggakan_pokok', 'tunggakan_bunga', 'tunggakan_pinalti',
    'os', 'nasabah', 'kolektibilitas_lancar', 'kolektibilitas_dpk',
    'kolektibilitas_kurang_lancar', 'kolektibilitas_diragukan', 'kolektibilitas_macet',
}

DATE_FIELDS = INTEGER_FIELDS = BOOLEAN_FIELDS = set()


def _parse_date(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        parsed = pd.to_datetime(value, errors='coerce')
        return None if pd.isna(parsed) else parsed.date()
    except (ValueError, TypeError):
        return None


def _parse_decimal(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        if isinstance(value, str):
            value = value.replace(',', '').strip()
            if not value:
                return None
        return Decimal(value)
    except (InvalidOperation, ValueError, TypeError):
        return None


def _parse_int(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def _parse_string(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ''
    result = str(value).strip()
    return '' if result in ['None', 'none', 'NONE'] else result


def _parse_periode(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ''
    if isinstance(value, pd.Timestamp) or hasattr(value, 'strftime') and not isinstance(value, str):
        return value.strftime('%d/%m/%Y')
    return str(value).strip() if isinstance(value, str) else str(value).strip()


def _parse_date_string(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ''
    
    if isinstance(value, (int, float)) and value == 0:
        return '0'
    
    if isinstance(value, str):
        value_clean = value.strip()
        if value_clean == '0':
            return '0'
        if not value_clean or value_clean == '0.0':
            return ''
        if '/' in value_clean:
            parts = value_clean.split('/')
            if len(parts) == 3 and all(p.isdigit() for p in parts):
                return value_clean
        
        # Try to parse any date format and convert to MM/DD/YYYY
        try:
            # Try multiple date formats
            parsed = pd.to_datetime(value_clean, errors='coerce', infer_datetime_format=True)
            if pd.notna(parsed):
                return parsed.strftime('%m/%d/%Y')
        except:
            pass
        
        # If can't parse, return as-is
        return value_clean
    
    # Fallback: convert to string
    return str(value).strip()


def _parse_boolean(value):
    """
    Parse boolean value dari Excel.
    Accepts: TRUE, FALSE, True, False, true, false, 1, 0, Yes, No, Y, N
    Returns: True, False, or None
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    
    # If already boolean
    if isinstance(value, bool):
        return value
    
    # Convert to string and normalize
    str_value = str(value).strip().upper()
    
    # True values
    if str_value in ['TRUE', '1', 'YES', 'Y', 'T']:
        return True
    
    # False values
    if str_value in ['FALSE', '0', 'NO', 'N', 'F']:
        return False
    
    # Invalid value
    return None


def validate_file_structure(file_path):
    """
    Validasi struktur file dan return sample data untuk preview.
    STRICT VALIDATION: Hanya menerima format kolom dengan spasi (tidak ada keringanan underscore).
    
    Args:
        file_path: Path ke file yang akan divalidasi
    
    Returns:
        dict: {
            'valid': bool,
            'sample_data': list of dicts (10 rows),
            'missing_columns': list,
            'extra_columns': list,
            'column_mapping': dict
        }
    """
    try:
        file_ext = file_path.lower()[file_path.rfind('.'):]
        
        # Baca file
        if file_ext == '.csv':
            df = pd.read_csv(file_path, dtype={'NOMOR REKENING': str}, nrows=10)
        elif file_ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path, dtype={'NOMOR REKENING': str}, nrows=10)
        else:
            return {
                'valid': False,
                'error': 'Format file tidak didukung. Gunakan .csv, .xlsx, atau .xls'
            }
        
        # Normalisasi nama kolom
        df.columns = [str(col).strip().upper() for col in df.columns]
        
        # Expected columns dalam urutan yang diinginkan user
        expected_columns_ordered = [
            'PERIODE',
            'KANCA',
            'KODE UKER',
            'UKER',
            'LN TYPE',
            'NOMOR REKENING',
            'NAMA DEBITUR',
            'PLAFON',
            'NEXT PMT DATE',
            'NEXT INT PMT DATE',
            'RATE',
            'TGL MENUNGGAK',
            'TGL REALISASI',
            'TGL JATUH TEMPO',
            'JANGKA WAKTU',
            'FLAG RESTRUK',
            'CIFNO',
            'KOLEKTIBILITAS LANCAR',
            'KOLEKTIBILITAS DPK',
            'KOLEKTIBILITAS KURANG LANCAR',
            'KOLEKTIBILITAS DIRAGUKAN',
            'KOLEKTIBILITAS MACET',
            'TUNGGAKAN POKOK',
            'TUNGGAKAN BUNGA',
            'TUNGGAKAN PINALTI',
            'CODE',
            'DESCRIPTION',
            'KOL_ADK',
            'PN RM',
            'NAMA RM',
            'OS',
            'NASABAH',
            'DUB NASABAH'
        ]
        
        expected_columns = set(expected_columns_ordered)
        actual_columns = set(df.columns)
        
        # STRICT VALIDATION: Hanya terima format dengan spasi (sesuai expected_columns_ordered)
        # Kolom yang hilang (tidak ada exact match)
        missing_columns = expected_columns - actual_columns
        
        # Kolom extra (ada di file tapi tidak ada di expected)
        extra_columns = actual_columns - expected_columns
        
        # Prepare sample data dengan status validasi per kolom
        # IMPORTANT: Urutan kolom sesuai expected_columns_ordered
        # Status kolom: 'ok' = kolom ada di file (exact match), 'missing' = kolom tidak ada
        sample_data = []
        for index, row in df.iterrows():
            row_data = {}
            for col in expected_columns_ordered:  # Gunakan urutan yang sudah ditentukan
                if col in actual_columns:
                    # Kolom ada di file Excel dengan nama yang persis - status OK (hijau)
                    value = row.get(col)
                    # Apply TRIM untuk string values
                    if pd.notna(value) and isinstance(value, str):
                        value = value.strip()
                    row_data[col] = {
                        'value': value,
                        'status': 'ok'  # Hijau: kolom ada dengan nama yang benar
                    }
                else:
                    # Kolom tidak ada di file Excel (atau nama tidak sesuai) - status MISSING (merah)
                    row_data[col] = {
                        'value': '-',
                        'status': 'missing'  # Merah: kolom tidak ada atau nama salah
                    }
            sample_data.append(row_data)
        
        
        return {
            'valid': len(missing_columns) == 0,
            'sample_data': sample_data,
            'missing_columns': list(missing_columns),
            'extra_columns': list(extra_columns),
            'expected_columns': expected_columns_ordered,  # Gunakan list yang sudah terurut
            'actual_columns': list(actual_columns),
            'total_rows': len(df)  # From sample only, actual may be more
        }
        
    except Exception as e:
        return {
            'valid': False,
            'error': str(e)
        }


def process_uploaded_file(upload_history):
    """
    Process uploaded file dan simpan ke database
    
    Args:
        upload_history: UploadHistory instance
    
    Returns:
        dict: Result dengan informasi proses
    """
    try:
        file_path = upload_history.file_path.path
        file_ext = file_path.lower()[file_path.rfind('.'):]
        
        # Baca file berdasarkan ekstensi
        # PENTING: dtype=str untuk kolom yang harus preserve leading zeros
        # Jangan parse dates otomatis, kita akan handle manual
        if file_ext == '.csv':
            df = pd.read_csv(file_path, dtype={'NOMOR REKENING': str, 'NOMOR_REKENING': str}, parse_dates=False)
        elif file_ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path, dtype={'NOMOR REKENING': str, 'NOMOR_REKENING': str})
        else:
            return {
                'success': False,
                'error': 'Format file tidak didukung'
            }
        
        df.columns = [str(col).strip().upper() for col in df.columns]
        
        required_columns = ['PERIODE', 'NOMOR REKENING', 'CIFNO']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return {
                'success': False,
                'error': f'Kolom yang diperlukan tidak ditemukan: {", ".join(missing_columns)}. Kolom yang ada: {", ".join(df.columns)}'
            }

        total_rows = len(df)
        successful_rows = 0
        failed_rows = 0
        error_messages = []
        
        # Process setiap baris
        for index, row in df.iterrows():
            try:
                record = {}

                # Process setiap kolom berdasarkan COLUMN_FIELD_MAP (format dengan spasi)
                for source_column, target_field in COLUMN_FIELD_MAP.items():
                    # Skip jika kolom tidak ada di DataFrame
                    if source_column not in df.columns:
                        continue
                    
                    raw_value = row.get(source_column)

                    if pd.notna(raw_value) and isinstance(raw_value, str):
                        raw_value = raw_value.strip()

                    if target_field == PERIODE_FIELD:
                        record[target_field] = _parse_periode(raw_value)
                    elif target_field in DATE_FIELDS:
                        record[target_field] = _parse_date(raw_value)
                    elif target_field in DATE_STRING_FIELDS:
                        record[target_field] = _parse_date_string(raw_value)
                    elif target_field in DECIMAL_FIELDS:
                        record[target_field] = _parse_decimal(raw_value)
                    elif target_field in INTEGER_FIELDS:
                        record[target_field] = _parse_int(raw_value)
                    elif target_field in BOOLEAN_FIELDS:
                        record[target_field] = _parse_boolean(raw_value)
                    else:
                        record[target_field] = _parse_string(raw_value)

                nomor_rekening = record.get('nomor_rekening')
                if not nomor_rekening:
                    # Debug: cek apakah kolom NOMOR REKENING ada di file
                    if 'NOMOR REKENING' not in df.columns:
                        raise ValueError('Kolom "NOMOR REKENING" tidak ditemukan di file Excel. Kolom yang tersedia: ' + ', '.join(df.columns))
                    else:
                        raise ValueError(f'Nomor rekening tidak boleh kosong. Nilai: {row.get("NOMOR REKENING")}')
                
                # Ensure nomor_rekening is string and preserve leading zeros
                # Convert float/int to string with proper formatting
                if isinstance(nomor_rekening, (int, float)):
                    # Format as integer string (no decimal point)
                    nomor_rekening = str(int(nomor_rekening))
                else:
                    nomor_rekening = str(nomor_rekening).strip()
                
                # Pad with zeros if needed (18 digits for BRI account numbers)
                if nomor_rekening.isdigit() and len(nomor_rekening) < 18:
                    nomor_rekening = nomor_rekening.zfill(18)
                
                record['nomor_rekening'] = nomor_rekening

                periode = record.get('periode') or ''
                if not periode:
                    if 'PERIODE' not in df.columns:
                        raise ValueError('Kolom "PERIODE" tidak ditemukan di file Excel')
                    else:
                        raise ValueError(f'Periode tidak boleh kosong. Nilai: {row.get("PERIODE")}')

                cif_no = record.get('cif_no') or ''
                if not cif_no:
                    if 'CIFNO' not in df.columns:
                        raise ValueError('Kolom "CIFNO" tidak ditemukan di file Excel')
                    else:
                        raise ValueError(f'CIF tidak boleh kosong. Nilai: {row.get("CIFNO")}')

                record['periode'] = periode
                record['cif_no'] = cif_no

                # Truncate VARCHAR fields to prevent "value too long" errors
                # Based on model field max_length definitions
                MAX_LENGTHS = {
                    'periode': 20,
                    'kanca': 100,
                    'kode_uker': 10,
                    'uker': 100,
                    'ln_type': 10,
                    'nomor_rekening': 100,
                    'nama_debitur': 100,
                    'next_pmt_date': 20,
                    'next_int_pmt_date': 20,
                    'tgl_menunggak': 20,
                    'tgl_realisasi': 20,
                    'tgl_jatuh_tempo': 20,
                    'jangka_waktu': 10,
                    'flag_restruk': 10,
                    'cif_no': 100,
                    'kolektibilitas_lancar': 100,
                    'kolektibilitas_dpk': 100,
                    'kolektibilitas_kurang_lancar': 100,
                    'kolektibilitas_diragukan': 100,
                    'kolektibilitas_macet': 100,
                    'code': 100,
                    'description': 255,
                    'kol_adk': 10,
                    'pn_rm': 20,
                    'nama_rm': 100,
                    'dub_nasabah': 10,
                }
                
                for field_name, max_length in MAX_LENGTHS.items():
                    if field_name in record and isinstance(record[field_name], str):
                        if len(record[field_name]) > max_length:
                            record[field_name] = record[field_name][:max_length]

                LW321.objects.create(**record)
                successful_rows += 1
                
            except Exception as e:
                failed_rows += 1
                error_messages.append(f"Row {index + 1}: {str(e)}")
                continue
        
        return {
            'success': True,
            'total_rows': total_rows,
            'successful_rows': successful_rows,
            'failed_rows': failed_rows,
            'errors': error_messages,
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'total_rows': 0,
            'successful_rows': 0,
            'failed_rows': 0
        }


def process_data_for_dashboard(data_type, sub_type=None, date_range=None):
    """
    Olah data untuk dashboard
    
    Args:
        data_type: Tipe dashboard (os, summary, grafik_harian)
        sub_type: Sub tipe (medium_only, konsol, only)
        date_range: Range tanggal
    
    Returns:
        dict: Processed data
    """
    # TODO: Implementasi logic pengolahan data sesuai kebutuhan dashboard
    # Ini adalah placeholder
    
    processed_data = {
        'data_type': data_type,
        'sub_type': sub_type,
        'date_range': date_range,
        'data': {}
    }
    
    return processed_data


# ==================== KOMITMEN UTILITIES ====================

def compare_komitmen_data(new_df, periode):
    """
    Compare new upload with existing data to show preview of changes
    Uses INDEX-BASED reading from DataFrame
    
    Args:
        new_df: pandas DataFrame with new data (index-based, no headers)
        periode: datetime.date object
    
    Returns:
        dict dengan keys:
        - is_new: bool (True jika belum ada data untuk periode ini)
        - new_rows: int (jumlah uker baru)
        - updated_rows: int (jumlah uker yang akan di-update)
        - deleted_rows: int (jumlah uker yang akan dihapus)
        - changes: list of dict (sample changes untuk preview)
        - existing_upload: KomitmenUpload object or None
    """
    from dashboard.models import KomitmenData, KomitmenUpload
    from data_management.validators import COLUMN_INDICES, CLOSED_UKER_CODES, clean_numeric_value
    
    # Filter out closed uker codes from new data
    new_df = new_df[~new_df[COLUMN_INDICES['kode_uker']].astype(str).str.strip().isin(CLOSED_UKER_CODES)].copy()
    
    try:
        existing_upload = KomitmenUpload.objects.get(periode=periode)
        existing_qs = KomitmenData.objects.filter(periode=periode)
        
        if existing_qs.count() == 0:
            return {
                'is_new': True,
                'new_rows': len(new_df),
                'updated_rows': 0,
                'deleted_rows': 0,
                'changes': [],
                'existing_upload': None
            }
        
        # Convert existing data to dict for comparison
        existing_dict = {}
        for data in existing_qs:
            existing_dict[str(data.kode_uker)] = {
                'kur_os': float(data.kur_os) if data.kur_os else 0,
                'kur_pl': float(data.kur_pl) if data.kur_pl else 0,
                'small_deb': float(data.small_deb) if data.small_deb else 0,
                'nama_uker': data.nama_uker,
            }
        
        # Compare - using index-based reading
        new_ukers = set(new_df[COLUMN_INDICES['kode_uker']].astype(str).str.strip())
        old_ukers = set(existing_dict.keys())
        
        changes = []
        for uker in new_ukers & old_ukers:  # Intersection
            new_row = new_df[new_df[COLUMN_INDICES['kode_uker']].astype(str).str.strip() == uker].iloc[0]
            old_data = existing_dict[uker]
            
            # Check sample columns
            new_kur_os = clean_numeric_value(new_row[COLUMN_INDICES['kur_os']]) or 0
            old_kur_os = old_data['kur_os']
            
            if abs(new_kur_os - old_kur_os) > 0.01:  # Changed
                changes.append({
                    'uker': old_data['nama_uker'],
                    'kode_uker': uker,
                    'column': 'KUR RITEL OS',
                    'old_value': old_kur_os,
                    'new_value': new_kur_os
                })
            
            if len(changes) >= 10:  # Limit to 10 sample changes
                break
        
        return {
            'is_new': False,
            'new_rows': len(new_ukers - old_ukers),
            'updated_rows': len(new_ukers & old_ukers),
            'deleted_rows': len(old_ukers - new_ukers),
            'changes': changes,
            'existing_upload': existing_upload
        }
        
    except KomitmenUpload.DoesNotExist:
        return {
            'is_new': True,
            'new_rows': len(new_df),
            'updated_rows': 0,
            'deleted_rows': 0,
            'changes': [],
            'existing_upload': None
        }


def save_komitmen_data(df, periode, upload_obj):
    """
    Save komitmen data from DataFrame to database
    Uses INDEX-BASED reading from DataFrame
    
    Args:
        df: pandas DataFrame (cleaned data without total rows, index-based)
        periode: datetime.date object
        upload_obj: KomitmenUpload instance
    
    Returns:
        int: Number of rows saved
    """
    from dashboard.models import KomitmenData
    from data_management.validators import COLUMN_INDICES, CLOSED_UKER_CODES, clean_numeric_value
    
    # Delete existing data for this periode
    KomitmenData.objects.filter(periode=periode).delete()
    
    # Prepare bulk create list
    komitmen_list = []
    skipped_closed = 0
    
    for _, row in df.iterrows():
        kode_uker = str(row[COLUMN_INDICES['kode_uker']]).strip()
        
        # Skip if kode_uker is empty
        if not kode_uker or kode_uker == 'nan':
            continue
        
        # Skip if kode_uker is closed
        if kode_uker in CLOSED_UKER_CODES:
            skipped_closed += 1
            continue
        
        komitmen_obj = KomitmenData(
            upload=upload_obj,
            periode=periode,
            kode_kanca=str(row[COLUMN_INDICES['kode_kanca']]).strip(),
            kode_uker=kode_uker,
            nama_kanca=str(row[COLUMN_INDICES['nama_kanca']]).strip(),
            nama_uker=str(row[COLUMN_INDICES['nama_uker']]).strip(),
            
            # KUR RITEL
            kur_deb=clean_numeric_value(row[COLUMN_INDICES['kur_deb']]),
            kur_os=clean_numeric_value(row[COLUMN_INDICES['kur_os']]),
            kur_pl=clean_numeric_value(row[COLUMN_INDICES['kur_pl']]),
            kur_npl=clean_numeric_value(row[COLUMN_INDICES['kur_npl']]),
            kur_dpk=clean_numeric_value(row[COLUMN_INDICES['kur_dpk']]),
            
            # SMALL SD 5M
            small_deb=clean_numeric_value(row[COLUMN_INDICES['small_deb']]),
            small_os=clean_numeric_value(row[COLUMN_INDICES['small_os']]),
            small_pl=clean_numeric_value(row[COLUMN_INDICES['small_pl']]),
            small_npl=clean_numeric_value(row[COLUMN_INDICES['small_npl']]),
            small_dpk=clean_numeric_value(row[COLUMN_INDICES['small_dpk']]),
            
            # KECIL NCC
            kecil_ncc_deb=clean_numeric_value(row[COLUMN_INDICES['kecil_ncc_deb']]),
            kecil_ncc_os=clean_numeric_value(row[COLUMN_INDICES['kecil_ncc_os']]),
            kecil_ncc_pl=clean_numeric_value(row[COLUMN_INDICES['kecil_ncc_pl']]),
            kecil_ncc_npl=clean_numeric_value(row[COLUMN_INDICES['kecil_ncc_npl']]),
            kecil_ncc_dpk=clean_numeric_value(row[COLUMN_INDICES['kecil_ncc_dpk']]),
            
            # KECIL CC
            kecil_cc_deb=clean_numeric_value(row[COLUMN_INDICES['kecil_cc_deb']]),
            kecil_cc_os=clean_numeric_value(row[COLUMN_INDICES['kecil_cc_os']]),
            kecil_cc_pl=clean_numeric_value(row[COLUMN_INDICES['kecil_cc_pl']]),
            kecil_cc_npl=clean_numeric_value(row[COLUMN_INDICES['kecil_cc_npl']]),
            kecil_cc_dpk=clean_numeric_value(row[COLUMN_INDICES['kecil_cc_dpk']]),
        )
        
        komitmen_list.append(komitmen_obj)
    
    # Bulk create
    KomitmenData.objects.bulk_create(komitmen_list, batch_size=500)
    
    # Log skipped rows if any
    if skipped_closed > 0:
        print(f"ℹ️  Skipped {skipped_closed} rows from closed uker codes")
    
    return len(komitmen_list)
