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
    'PN RM': 'pn_rm',  # Ganti nama kolom
    'NAMA RM': 'nama_rm',
    'OS': 'os',  # Kolom baru, berisi angka
}

# Alternative column names (dengan underscore) - untuk fleksibilitas user
COLUMN_FIELD_MAP_ALTERNATIVE = {
    'KODE_UKER': 'kode_uker',
    'LN_TYPE': 'ln_type',
    'NOMOR_REKENING': 'nomor_rekening',
    'NAMA_DEBITUR': 'nama_debitur',
    'NEXT_PMT_DATE': 'next_pmt_date',
    'NEXT_INT_PMT_DATE': 'next_int_pmt_date',
    'TGL_MENUNGGAK': 'tgl_menunggak',
    'TGL_REALISASI': 'tgl_realisasi',
    'TGL_JATUH_TEMPO': 'tgl_jatuh_tempo',
    'JANGKA_WAKTU': 'jangka_waktu',
    'FLAG_RESTRUK': 'flag_restruk',
    'KOLEKTIBILITAS_LANCAR': 'kolektibilitas_lancar',
    'KOLEKTIBILITAS_DPK': 'kolektibilitas_dpk',
    'KOLEKTIBILITAS_KURANG_LANCAR': 'kolektibilitas_kurang_lancar',
    'KOLEKTIBILITAS_DIRAGUKAN': 'kolektibilitas_diragukan',
    'KOLEKTIBILITAS_MACET': 'kolektibilitas_macet',
    'TUNGGAKAN_POKOK': 'tunggakan_pokok',
    'TUNGGAKAN_BUNGA': 'tunggakan_bunga',
    'TUNGGAKAN_PINALTI': 'tunggakan_pinalti',
    'PN_RM': 'pn_rm',
    'NAMA_RM': 'nama_rm',
}

# Gabungkan kedua mapping untuk lookup
COLUMN_FIELD_MAP_COMBINED = {**COLUMN_FIELD_MAP, **COLUMN_FIELD_MAP_ALTERNATIVE}

DATE_FIELDS = {
    'next_pmt_date',
    'next_int_pmt_date',
    'tgl_menunggak',
    'tgl_realisasi',
    'tgl_jatuh_tempo',
}

DECIMAL_FIELDS = {
    'plafon',
    'rate',
    'tunggakan_pokok',
    'tunggakan_bunga',
    'tunggakan_pinalti',
    'os',  # Kolom OS baru (angka)
}

INTEGER_FIELDS = {
    'jangka_waktu',
}


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
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ''
    # TRIM: Strip whitespace dari depan dan belakang
    return str(value).strip()


def has_column(col_name, columns_list):
    """
    Helper function untuk cek apakah kolom ada dengan fleksibilitas format.
    Support format dengan spasi atau underscore.
    
    Args:
        col_name: Nama kolom yang dicari
        columns_list: List kolom yang tersedia
    
    Returns:
        bool: True jika kolom ditemukan (dengan format spasi atau underscore)
    """
    if col_name in columns_list:
        return True
    if col_name.replace(' ', '_') in columns_list:
        return True
    if col_name.replace('_', ' ') in columns_list:
        return True
    return False


def validate_file_structure(file_path):
    """
    Validasi struktur file dan return sample data untuk preview
    
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
            'OS'
        ]
        
        expected_columns = set(expected_columns_ordered)
        actual_columns = set(df.columns)
        
        # Fungsi helper untuk mengecek apakah kolom ada (termasuk alternatif underscore)
        def find_column_in_file(expected_col, actual_cols):
            """
            Cari kolom di file, support format spasi atau underscore
            Returns: (found_column_name, is_found)
            """
            # Cek exact match
            if expected_col in actual_cols:
                return expected_col, True
            
            # Cek alternative dengan underscore
            alt_col = expected_col.replace(' ', '_')
            if alt_col in actual_cols:
                return alt_col, True
            
            return None, False
        
        # Mapping kolom yang ditemukan
        found_columns = {}  # expected_col -> actual_col (di file)
        for col in expected_columns_ordered:
            found_col, is_found = find_column_in_file(col, actual_columns)
            if is_found:
                found_columns[col] = found_col
        
        # Kolom yang hilang (tidak ada dalam format spasi atau underscore)
        missing_columns = set([col for col in expected_columns_ordered if col not in found_columns])
        
        # Kolom extra (ada di file tapi tidak diharapkan)
        all_expected_variations = set(expected_columns_ordered)
        for col in expected_columns_ordered:
            all_expected_variations.add(col.replace(' ', '_'))
        extra_columns = actual_columns - all_expected_variations
        
        # Prepare sample data dengan status validasi per kolom
        # IMPORTANT: Urutan kolom sesuai expected_columns_ordered
        # Status kolom: 'ok' = kolom ada di file, 'missing' = kolom tidak ada di file
        sample_data = []
        for index, row in df.iterrows():
            row_data = {}
            for col in expected_columns_ordered:  # Gunakan urutan yang sudah ditentukan
                if col in found_columns:
                    # Kolom ada di file Excel (dengan format spasi atau underscore) - status OK (hijau)
                    actual_col = found_columns[col]
                    value = row.get(actual_col)
                    # Apply TRIM untuk string values
                    if pd.notna(value) and isinstance(value, str):
                        value = value.strip()
                    row_data[col] = {
                        'value': value,
                        'status': 'ok'  # Hijau: kolom ada
                    }
                else:
                    # Kolom tidak ada di file Excel - status MISSING (merah)
                    row_data[col] = {
                        'value': '-',
                        'status': 'missing'  # Merah: kolom tidak ada
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
        if file_ext == '.csv':
            df = pd.read_csv(file_path, dtype={'NOMOR REKENING': str, 'NOMOR_REKENING': str})
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
        
        # Check kolom yang diperlukan (support format spasi atau underscore)
        required_columns_check = []
        for req_col in ['PERIODE', 'NOMOR REKENING', 'CIFNO']:
            col_exists = has_column(req_col, df.columns)
            print(f"[DEBUG] Checking '{req_col}': {col_exists}")
            if not col_exists:
                required_columns_check.append(req_col)
        
        if required_columns_check:
            print(f"[DEBUG] Missing columns: {required_columns_check}")
            return {
                'success': False,
                'error': f'Kolom yang diperlukan tidak ditemukan: {", ".join(required_columns_check)}. Kolom yang ada: {", ".join(df.columns)}'
            }

        total_rows = len(df)
        successful_rows = 0
        failed_rows = 0
        error_messages = []
        
        # Process setiap baris
        for index, row in df.iterrows():
            try:
                record = {}

                # Gunakan COLUMN_FIELD_MAP_COMBINED untuk support format spasi dan underscore
                for source_column, target_field in COLUMN_FIELD_MAP_COMBINED.items():
                    # Skip jika kolom tidak ada di DataFrame
                    if source_column not in df.columns:
                        continue
                    
                    raw_value = row.get(source_column)

                    # Apply TRIM untuk semua string values sebelum parsing
                    if pd.notna(raw_value) and isinstance(raw_value, str):
                        raw_value = raw_value.strip()

                    if target_field in DATE_FIELDS:
                        record[target_field] = _parse_date(raw_value)
                    elif target_field in DECIMAL_FIELDS:
                        record[target_field] = _parse_decimal(raw_value)
                    elif target_field in INTEGER_FIELDS:
                        record[target_field] = _parse_int(raw_value)
                    else:
                        record[target_field] = _parse_string(raw_value)

                nomor_rekening = record.get('nomor_rekening')
                if not nomor_rekening:
                    # Debug: cek apakah kolom NOMOR REKENING ada di file (format spasi atau underscore)
                    if not has_column('NOMOR REKENING', df.columns):
                        raise ValueError('Kolom "NOMOR REKENING" atau "NOMOR_REKENING" tidak ditemukan di file Excel. Kolom yang tersedia: ' + ', '.join(df.columns))
                    else:
                        # Cari actual column name
                        actual_col = None
                        if 'NOMOR REKENING' in df.columns:
                            actual_col = 'NOMOR REKENING'
                        elif 'NOMOR_REKENING' in df.columns:
                            actual_col = 'NOMOR_REKENING'
                        raise ValueError(f'Nomor rekening tidak boleh kosong. Nilai: {row.get(actual_col) if actual_col else "N/A"}')
                
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
                    if not has_column('PERIODE', df.columns):
                        raise ValueError('Kolom "PERIODE" tidak ditemukan di file Excel')
                    else:
                        raise ValueError(f'Periode tidak boleh kosong. Nilai: {row.get("PERIODE")}')

                cif_no = record.get('cif_no') or ''
                if not cif_no:
                    if not has_column('CIFNO', df.columns):
                        raise ValueError('Kolom "CIFNO" tidak ditemukan di file Excel')
                    else:
                        # Cari actual column name
                        actual_cif = 'CIFNO' if 'CIFNO' in df.columns else 'CIF_NO' if 'CIF_NO' in df.columns else None
                        raise ValueError(f'CIF tidak boleh kosong. Nilai: {row.get(actual_cif) if actual_cif else "N/A"}')

                record['periode'] = periode
                record['cif_no'] = cif_no

                # Selalu insert setiap row sebagai record baru
                # Setiap upload file = data baru ditambahkan (append-only)
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
