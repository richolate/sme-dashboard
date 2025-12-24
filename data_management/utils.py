import pandas as pd
from decimal import Decimal, InvalidOperation
from django.utils import timezone
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


# Fields yang sekarang menjadi VARCHAR (tidak perlu parsing khusus)
# next_pmt_date, next_int_pmt_date, tgl_menunggak, tgl_realisasi, tgl_jatuh_tempo
# semuanya sudah menjadi CharField, jadi tidak perlu DATE_FIELDS lagi
DATE_FIELDS = set()  # Kosongkan karena semua tanggal sudah jadi varchar

# Date string fields - perlu preserve format MM/DD/YYYY
DATE_STRING_FIELDS = {
    'next_pmt_date',
    'next_int_pmt_date',
    'tgl_menunggak',
    'tgl_realisasi',
    'tgl_jatuh_tempo',
}

# Periode field - needs special format: DD-Mon-YY (e.g., 30-Nov-25)
PERIODE_FIELD = 'periode'

DECIMAL_FIELDS = {
    'plafon',
    'rate',
    'tunggakan_pokok',
    'tunggakan_bunga',
    'tunggakan_pinalti',
    'os',  # Kolom OS baru (angka)
    'nasabah',  # Kolom NASABAH (angka)
    'kolektibilitas_lancar',
    'kolektibilitas_dpk',
    'kolektibilitas_kurang_lancar',
    'kolektibilitas_diragukan',
    'kolektibilitas_macet',
}

# INTEGER_FIELDS juga dikosongkan karena jangka_waktu sudah jadi varchar
INTEGER_FIELDS = set()  # Kosongkan karena jangka_waktu sudah jadi varchar

# BOOLEAN_FIELDS dikosongkan karena dub_nasabah sekarang VARCHAR
BOOLEAN_FIELDS = set()  # Kosongkan karena dub_nasabah sudah jadi varchar


def _parse_date(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None

    try:
        parsed = pd.to_datetime(value, errors='coerce')
        if pd.isna(parsed):
            return None
        return parsed.date()
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
    """
    Parse string value dari Excel.
    Untuk date fields, preserve format original (MM/DD/YYYY).
    Untuk nilai 'None' text, return empty string.
    Nilai 0 (numeric) tetap di-preserve.
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ''
    
    # TRIM: Strip whitespace dari depan dan belakang
    result = str(value).strip()
    
    # Jika hasilnya 'None' (text), return empty string
    # Tapi JANGAN convert numeric 0 ke empty string
    if result in ['None', 'none', 'NONE']:
        return ''
    
    return result


def _parse_periode(value):
    """
    Parse periode field - preserve original format from Excel.
    Typically: DD/MM/YYYY (e.g., 30/11/2025)
    
    Just clean and return the value as-is, don't convert format.
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ''
    
    # If it's a Timestamp, convert to DD/MM/YYYY format
    if isinstance(value, pd.Timestamp):
        return value.strftime('%d/%m/%Y')
    
    # If it has strftime (datetime-like), convert to DD/MM/YYYY
    if hasattr(value, 'strftime') and not isinstance(value, str):
        return value.strftime('%d/%m/%Y')
    
    # If it's a string, clean and return as-is
    if isinstance(value, str):
        value_clean = value.strip()
        return value_clean if value_clean else ''
    
    # Fallback: return as-is
    return str(value).strip()


def _parse_date_string(value):
    """
    Parse date string dengan preserve format MM/DD/YYYY.
    Jika value adalah datetime, convert ke MM/DD/YYYY.
    Jika value adalah 0 (integer/float), return "0" sebagai string.
    Jika value kosong atau None, return empty string.
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ''
    
    # Handle numeric 0 - return "0" sebagai string (bukan empty)
    if isinstance(value, (int, float)) and value == 0:
        return '0'
    
    # Handle string '0' - return "0" as-is (bukan empty)
    if isinstance(value, str) and value.strip() == '0':
        return '0'
    
    # Handle empty string
    if isinstance(value, str) and value.strip() in ['', '0.0']:
        return ''
    
    # If it's already a datetime object (from pandas), convert to MM/DD/YYYY
    if isinstance(value, pd.Timestamp):
        return value.strftime('%m/%d/%Y')
    
    # If it has strftime (datetime-like), convert to MM/DD/YYYY
    if hasattr(value, 'strftime') and not isinstance(value, str):
        return value.strftime('%m/%d/%Y')
    
    # If it's a string, check if it looks like a date
    if isinstance(value, str):
        value_clean = value.strip()
        
        # If empty, return empty
        if not value_clean:
            return ''
        
        # Check if already in MM/DD/YYYY format - preserve it
        if '/' in value_clean:
            parts = value_clean.split('/')
            if len(parts) == 3 and all(p.isdigit() for p in parts):
                # Already in slash format, assume it's correct
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
        
        # Normalisasi nama kolom (hilangkan spasi depan/belakang dan ubah ke uppercase)
        df.columns = [str(col).strip().upper() for col in df.columns]
        
        # Debug: Log kolom yang ditemukan
        print(f"[DEBUG] Kolom di file Excel: {list(df.columns)}")
        
        # Check kolom yang diperlukan (STRICT: hanya format spasi)
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

                    # Apply TRIM untuk semua string values sebelum parsing
                    if pd.notna(raw_value) and isinstance(raw_value, str):
                        raw_value = raw_value.strip()

                    # Debug: Log date field values
                    if target_field in DATE_STRING_FIELDS and index < 3:
                        print(f"[DEBUG] Row {index}, Field {target_field}: raw_value={repr(raw_value)} (type: {type(raw_value).__name__})")

                    # Parse periode field to DD-Mon-YY format
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
                
                # Truncate string fields if they exceed max_length
                for field_name, max_length in MAX_LENGTHS.items():
                    if field_name in record and isinstance(record[field_name], str):
                        if len(record[field_name]) > max_length:
                            original_value = record[field_name]
                            record[field_name] = record[field_name][:max_length]
                            print(f"[WARNING] Row {index + 1}, Field {field_name}: Truncated from {len(original_value)} to {max_length} chars")
                            print(f"  Original: {original_value[:100]}...")
                            print(f"  Truncated: {record[field_name]}")

                # Selalu insert setiap row sebagai record baru
                # Setiap upload file = data baru ditambahkan (append-only)
                LW321.objects.create(**record)
                
                successful_rows += 1
                
            except Exception as e:
                failed_rows += 1
                error_msg = f"Row {index + 1}: {str(e)}"
                error_messages.append(error_msg)
                print(f"[ERROR] {error_msg}")
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
