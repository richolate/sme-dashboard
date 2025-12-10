import pandas as pd
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from dashboard.models import LW321


COLUMN_FIELD_MAP = {
    'PERIODE': 'periode',
    'KANCA': 'kanca',
    'KODE_UKER': 'kode_uker',
    'UKER': 'uker',
    'LN_TYPE': 'ln_type',
    'NOMOR_REKENING': 'nomor_rekening',
    'NAMA_DEBITUR': 'nama_debitur',
    'PLAFON': 'plafon',
    'NEXT_PMT_DATE': 'next_pmt_date',
    'NEXT_INT_PMT_DATE': 'next_int_pmt_date',
    'RATE': 'rate',
    'TGL_MENUNGGAK': 'tgl_menunggak',
    'TGL_REALISASI': 'tgl_realisasi',
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
    'PN PENGELOLA SINGLEPN': 'pn_pengelola_singlepn',
    'PN PENGELOLA 1': 'pn_pengelola_1',
    'PN PEMRAKARSA': 'pn_pemrakarsa',
    'PN REFERRAL': 'pn_referral',
    'PN RESTRUK': 'pn_restruk',
    'PN PENGELOLA 2': 'pn_pengelola_2',
    'PN PEMUTUS': 'pn_pemutus',
    'PN CRM': 'pn_crm',
    'PN RM REFERRAL NAIK SEGMENTASI': 'pn_rm_referral_naik_segmentasi',
    'PN RM CRR': 'pn_rm_crr',
}

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
    return str(value).strip()


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
        if file_ext == '.csv':
            df = pd.read_csv(file_path)
        elif file_ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        else:
            return {
                'success': False,
                'error': 'Format file tidak didukung'
            }
        
        # Normalisasi nama kolom (hilangkan spasi depan/belakang dan ubah ke uppercase)
        df.columns = [str(col).strip().upper() for col in df.columns]

        total_rows = len(df)
        successful_rows = 0
        failed_rows = 0
        error_messages = []
        
        # Process setiap baris
        for index, row in df.iterrows():
            try:
                record = {}

                for source_column, target_field in COLUMN_FIELD_MAP.items():
                    raw_value = row.get(source_column)

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
                    raise ValueError('Nomor rekening tidak boleh kosong')

                periode = record.get('periode') or ''
                if not periode:
                    raise ValueError('Periode tidak boleh kosong')

                cif_no = record.get('cif_no') or ''
                if not cif_no:
                    raise ValueError('CIF tidak boleh kosong')

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
