"""
Komitmen Helper Module - Functions to fetch and integrate komitmen data efficiently
"""

from datetime import datetime
from decimal import Decimal
from django.db.models import Q
from ..models import KomitmenData


def get_komitmen_for_month(year, month):
    """
    Ambil semua data komitmen untuk bulan tertentu.
    Return dictionary dengan key (kode_uker) untuk akses cepat.
    
    Args:
        year: int - Tahun
        month: int - Bulan (1-12)
    
    Returns:
        dict: {
            kode_uker: {
                'kode_kanca': str,
                'nama_kanca': str,
                'nama_uker': str,
                'kur': {
                    'deb': Decimal, 'os': Decimal, 'pl': Decimal, 
                    'npl': Decimal, 'dpk': Decimal
                },
                'small': {
                    'deb': Decimal, 'os': Decimal, 'pl': Decimal, 
                    'npl': Decimal, 'dpk': Decimal
                },
                'ncc': {
                    'deb': Decimal, 'os': Decimal, 'pl': Decimal, 
                    'npl': Decimal, 'dpk': Decimal
                },
                'cc': {
                    'deb': Decimal, 'os': Decimal, 'pl': Decimal, 
                    'npl': Decimal, 'dpk': Decimal
                }
            }
        }
    """
    # Filter by periode (year-month)
    komitmen_qs = KomitmenData.objects.filter(
        periode__year=year,
        periode__month=month
    ).select_related('upload')
    
    # Build dictionary untuk akses O(1)
    komitmen_dict = {}
    
    # Return nilai asli tanpa pembagian (dalam ribuan)
    # Display formatting akan dilakukan di template
    
    for data in komitmen_qs:
        komitmen_dict[data.kode_uker] = {
            'kode_kanca': data.kode_kanca,
            'nama_kanca': data.nama_kanca,
            'nama_uker': data.nama_uker,
            'kur': {
                'deb': data.kur_deb or Decimal('0'),
                'os': data.kur_os or Decimal('0'),
                'pl': data.kur_pl or Decimal('0'),
                'npl': data.kur_npl or Decimal('0'),
                'dpk': data.kur_dpk or Decimal('0'),
            },
            'small': {
                'deb': data.small_deb or Decimal('0'),
                'os': data.small_os or Decimal('0'),
                'pl': data.small_pl or Decimal('0'),
                'npl': data.small_npl or Decimal('0'),
                'dpk': data.small_dpk or Decimal('0'),
            },
            'ncc': {
                'deb': data.kecil_ncc_deb or Decimal('0'),
                'os': data.kecil_ncc_os or Decimal('0'),
                'pl': data.kecil_ncc_pl or Decimal('0'),
                'npl': data.kecil_ncc_npl or Decimal('0'),
                'dpk': data.kecil_ncc_dpk or Decimal('0'),
            },
            'cc': {
                'deb': data.kecil_cc_deb or Decimal('0'),
                'os': data.kecil_cc_os or Decimal('0'),
                'pl': data.kecil_cc_pl or Decimal('0'),
                'npl': data.kecil_cc_npl or Decimal('0'),
                'dpk': data.kecil_cc_dpk or Decimal('0'),
            }
        }
    
    return komitmen_dict



def get_komitmen_for_kanca_list(year, month):
    """
    Ambil data komitmen agregat per kanca untuk bulan tertentu.
    Aggregate semua uker dalam satu kanca.
    
    Args:
        year: int - Tahun
        month: int - Bulan (1-12)
    
    Returns:
        dict: {
            kode_kanca: {
                'nama_kanca': str,
                'kur': {'deb': Decimal, 'os': Decimal, ...},
                'small': {...},
                'ncc': {...},
                'cc': {...}
            }
        }
    """
    from django.db.models import Sum
    
    # Aggregate by kode_kanca
    komitmen_qs = KomitmenData.objects.filter(
        periode__year=year,
        periode__month=month
    ).values('kode_kanca', 'nama_kanca').annotate(
        # KUR
        kur_deb=Sum('kur_deb'),
        kur_os=Sum('kur_os'),
        kur_pl=Sum('kur_pl'),
        kur_npl=Sum('kur_npl'),
        kur_dpk=Sum('kur_dpk'),
        # SMALL
        small_deb=Sum('small_deb'),
        small_os=Sum('small_os'),
        small_pl=Sum('small_pl'),
        small_npl=Sum('small_npl'),
        small_dpk=Sum('small_dpk'),
        # NCC
        ncc_deb=Sum('kecil_ncc_deb'),
        ncc_os=Sum('kecil_ncc_os'),
        ncc_pl=Sum('kecil_ncc_pl'),
        ncc_npl=Sum('kecil_ncc_npl'),
        ncc_dpk=Sum('kecil_ncc_dpk'),
        # CC
        cc_deb=Sum('kecil_cc_deb'),
        cc_os=Sum('kecil_cc_os'),
        cc_pl=Sum('kecil_cc_pl'),
        cc_npl=Sum('kecil_cc_npl'),
        cc_dpk=Sum('kecil_cc_dpk'),
    )
    
    # Return nilai asli tanpa pembagian (dalam ribuan)
    # Display formatting akan dilakukan di template
    
    komitmen_dict = {}
    
    for data in komitmen_qs:
        komitmen_dict[data['kode_kanca']] = {
            'nama_kanca': data['nama_kanca'],
            'kur': {
                'deb': data['kur_deb'] or Decimal('0'),
                'os': data['kur_os'] or Decimal('0'),
                'pl': data['kur_pl'] or Decimal('0'),
                'npl': data['kur_npl'] or Decimal('0'),
                'dpk': data['kur_dpk'] or Decimal('0'),
            },
            'small': {
                'deb': data['small_deb'] or Decimal('0'),
                'os': data['small_os'] or Decimal('0'),
                'pl': data['small_pl'] or Decimal('0'),
                'npl': data['small_npl'] or Decimal('0'),
                'dpk': data['small_dpk'] or Decimal('0'),
            },
            'ncc': {
                'deb': data['ncc_deb'] or Decimal('0'),
                'os': data['ncc_os'] or Decimal('0'),
                'pl': data['ncc_pl'] or Decimal('0'),
                'npl': data['ncc_npl'] or Decimal('0'),
                'dpk': data['ncc_dpk'] or Decimal('0'),
            },
            'cc': {
                'deb': data['cc_deb'] or Decimal('0'),
                'os': data['cc_os'] or Decimal('0'),
                'pl': data['cc_pl'] or Decimal('0'),
                'npl': data['cc_npl'] or Decimal('0'),
                'dpk': data['cc_dpk'] or Decimal('0'),
            }
        }
    
    return komitmen_dict



def get_komitmen_value(komitmen_dict, kode_identifier, segment, metric):
    """
    Get komitmen value dari dictionary.
    Helper function untuk mengambil nilai dengan handling None/missing.
    
    Args:
        komitmen_dict: Dictionary hasil dari get_komitmen_for_month() atau get_komitmen_for_kanca_list()
        kode_identifier: kode_uker atau kode_kanca (string)
        segment: 'kur', 'small', 'ncc', atau 'cc'
        metric: 'deb', 'os', 'pl', 'npl', atau 'dpk'
    
    Returns:
        Decimal or None: Nilai komitmen, atau None jika tidak ada
    """
    if not komitmen_dict or kode_identifier not in komitmen_dict:
        return None
    
    data = komitmen_dict[kode_identifier]
    
    if segment not in data:
        return None
    
    if metric not in data[segment]:
        return None
    
    value = data[segment][metric]
    
    # Return None untuk 0 agar di template tampil sebagai "-"
    if value == 0 or value is None:
        return None
    
    return value


def aggregate_komitmen_regional(komitmen_dict, kode_kanca_list):
    """
    Aggregate komitmen untuk beberapa kanca (untuk regional/konsol).
    
    Args:
        komitmen_dict: Dictionary dari get_komitmen_for_kanca_list()
        kode_kanca_list: List of kode_kanca yang akan diaggregate
    
    Returns:
        dict: Aggregated komitmen {
            'kur': {'deb': Decimal, ...},
            'small': {...},
            'ncc': {...},
            'cc': {...}
        }
    """
    result = {
        'kur': {'deb': Decimal('0'), 'os': Decimal('0'), 'pl': Decimal('0'), 'npl': Decimal('0'), 'dpk': Decimal('0')},
        'small': {'deb': Decimal('0'), 'os': Decimal('0'), 'pl': Decimal('0'), 'npl': Decimal('0'), 'dpk': Decimal('0')},
        'ncc': {'deb': Decimal('0'), 'os': Decimal('0'), 'pl': Decimal('0'), 'npl': Decimal('0'), 'dpk': Decimal('0')},
        'cc': {'deb': Decimal('0'), 'os': Decimal('0'), 'pl': Decimal('0'), 'npl': Decimal('0'), 'dpk': Decimal('0')},
    }
    
    for kode_kanca in kode_kanca_list:
        if kode_kanca not in komitmen_dict:
            continue
        
        data = komitmen_dict[kode_kanca]
        
        for segment in ['kur', 'small', 'ncc', 'cc']:
            for metric in ['deb', 'os', 'pl', 'npl', 'dpk']:
                result[segment][metric] += data[segment][metric]
    
    return result


def check_komitmen_exists(year, month):
    """
    Check apakah ada data komitmen untuk bulan tertentu.
    
    Args:
        year: int
        month: int
    
    Returns:
        bool: True jika ada data komitmen, False jika tidak
    """
    return KomitmenData.objects.filter(
        periode__year=year,
        periode__month=month
    ).exists()
