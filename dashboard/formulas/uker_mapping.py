"""
Mapping KANCA (Kantor Cabang), UKER (Unit Kerja), dan KCP (Kantor Cabang Pembantu)
untuk Kanwil BRI Bandung

Struktur:
- KANCA/KC: Kantor Cabang (level utama)
- UKER: Unit Kerja (bisa KANCA atau KCP)
- KCP: Kantor Cabang Pembantu (sub-unit di bawah KANCA)
- RO: Regional Office

Cara Identifikasi:
- Jika KODE_UKER == KODE_KANCA → itu adalah KANCA/KC
- Jika KODE_UKER != KODE_KANCA → itu adalah KCP
- Nama KANCA dimulai dengan "KC "
- Nama KCP dimulai dengan "KCP "
"""

from typing import Dict, List, Tuple, Optional

# ==================================================================================
# MASTER DATA: KANCA (Kantor Cabang)
# Format: KODE_KANCA: NAMA_KANCA
# ==================================================================================
KANCA_MASTER: Dict[int, str] = {
    5: "KC Bandung AA",
    25: "KC Garut",
    28: "KC Indramayu",
    46: "KC Majalengka",
    75: "KC Purwakarta",
    92: "KC Sukabumi",
    94: "KC Sumedang",
    100: "KC Tasikmalaya",
    104: "KC Ciamis",
    105: "KC Cianjur",
    107: "KC Cirebon Kartini",
    123: "KC Subang",
    132: "KC Majalaya",
    133: "KC Kuningan",
    137: "KC Cimahi",
    161: "KC Singaparna",
    162: "KC Banjar",
    165: "KC Jatibarang",
    181: "KC Cibadak",
    286: "KC Bandung Dewi Sartika",
    337: "KC Bandung Naripan",
    354: "KC Bandung A.H. Nasution",
    355: "KC Pamanukan",
    389: "KC Bandung Martadinata",
    401: "KC Bandung Kopo",
    405: "KC Bandung Dago",
    406: "KC Cirebon Gunung Jati",
    407: "KC Bandung Sukarno Hatta",
    408: "KC Bandung Setiabudi",
    544: "KC Soreang",
}

# ==================================================================================
# MASTER DATA: UKER (Unit Kerja) - Lengkap dengan KANCA dan KCP
# Format: KODE_UKER: (NAMA_UKER, KODE_KANCA_INDUK)
# ==================================================================================
UKER_MASTER: Dict[int, Tuple[str, int]] = {
    # KC Bandung AA (KODE_KANCA: 5)
    5: ("KC Bandung AA", 5),
    675: ("KCP RAJAWALI BANDUNG", 5),
    
    # KC Garut (KODE_KANCA: 25)
    25: ("KC Garut", 25),
    1345: ("KCP GUNTUR", 25),
    1346: ("KCP CIKAJANG", 25),
    
    # KC Indramayu (KODE_KANCA: 28)
    28: ("KC Indramayu", 28),
    599: ("KCP Patrol", 28),
    
    # KC Majalengka (KODE_KANCA: 46)
    46: ("KC Majalengka", 46),
    1108: ("KCP ABDUL FATAH", 46),
    
    # KC Purwakarta (KODE_KANCA: 75)
    75: ("KC Purwakarta", 75),
    
    # KC Sukabumi (KODE_KANCA: 92)
    92: ("KC Sukabumi", 92),
    2162: ("KCP PASAR PELITA", 92),
    2229: ("KCP SURADE", 92),
    
    # KC Sumedang (KODE_KANCA: 94)
    94: ("KC Sumedang", 94),
    598: ("KCP BRI JATINANGOR", 94),
    
    # KC Tasikmalaya (KODE_KANCA: 100)
    100: ("KC Tasikmalaya", 100),
    1337: ("KCP CIKURUBUK", 100),
    1437: ("KCP CIAWI TASIKMALAYA", 100),
    
    # KC Ciamis (KODE_KANCA: 104)
    104: ("KC Ciamis", 104),
    
    # KC Cianjur (KODE_KANCA: 105)
    105: ("KC Cianjur", 105),
    517: ("KCP Cipanas", 105),
    2230: ("KCP CIRANJANG", 105),
    2231: ("KCP SUKANAGARA", 105),
    
    # KC Cirebon Kartini (KODE_KANCA: 107)
    107: ("KC Cirebon Kartini", 107),
    601: ("KCP Weru", 107),
    
    # KC Subang (KODE_KANCA: 123)
    123: ("KC Subang", 123),
    
    # KC Majalaya (KODE_KANCA: 132)
    132: ("KC Majalaya", 132),
    1139: ("KCP RANCAEKEK", 132),
    
    # KC Kuningan (KODE_KANCA: 133)
    133: ("KC Kuningan", 133),
    137: ("KC Cimahi", 133),  # Note: This appears to be UKER under Kuningan
    656: ("KCP PADALARANG", 133),
    
    # KC Cimahi (KODE_KANCA: 137) - Also appears as standalone KANCA
    1070: ("KCP CIJERAH", 137),
    1071: ("KCP CIMINDI", 137),
    
    # KC Singaparna (KODE_KANCA: 161)
    161: ("KC Singaparna", 161),
    
    # KC Banjar (KODE_KANCA: 162)
    162: ("KC Banjar", 162),
    542: ("KCP Pangandaran", 162),
    
    # KC Jatibarang (KODE_KANCA: 165)
    165: ("KC Jatibarang", 165),
    
    # KC Cibadak (KODE_KANCA: 181)
    181: ("KC Cibadak", 181),
    543: ("KCP Pelabuhan Ratu", 181),
    1355: ("KCP CICURUG", 181),
    286: ("KC Bandung Dewi Sartika", 181),  # Note: Also standalone KANCA
    650: ("KCP OTTO ISKANDARDINATA", 181),
    
    # KC Bandung Dewi Sartika (KODE_KANCA: 286)
    1077: ("KCP PETA", 286),
    1596: ("KCP TELKOM BANDUNG", 286),
    2202: ("KCP KOSAMBI BANDUNG", 286),
    
    # KC Bandung Naripan (KODE_KANCA: 337)
    337: ("KC Bandung Naripan", 337),
    1141: ("KCP SIMPANG BUAH BATU", 337),
    
    # KC Bandung A.H. Nasution (KODE_KANCA: 354)
    354: ("KC Bandung A.H. Nasution", 354),
    2105: ("KCP SUCI", 354),
    
    # KC Pamanukan (KODE_KANCA: 355)
    355: ("KC Pamanukan", 355),
    
    # KC Bandung Martadinata (KODE_KANCA: 389)
    389: ("KC Bandung Martadinata", 389),
    2104: ("KCP RIAU", 389),
    
    # KC Bandung Kopo (KODE_KANCA: 401)
    401: ("KC Bandung Kopo", 401),
    600: ("KCP SUMBER SARI", 401),
    2103: ("KCP Mekarwangi", 401),
    2155: ("KCP TAMAN KOPO INDAH", 401),
    2184: ("KCP TAMAN KOPO INDAH II", 401),
    
    # KC Bandung Dago (KODE_KANCA: 405)
    405: ("KC Bandung Dago", 405),
    593: ("KCP ITB", 405),
    
    # KC Cirebon Gunung Jati (KODE_KANCA: 406)
    406: ("KC Cirebon Gunung Jati", 406),
    1078: ("KCP SUMBER", 406),
    2128: ("KCP CILEDUG CIREBON", 406),
    
    # KC Bandung Sukarno Hatta (KODE_KANCA: 407)
    407: ("KC Bandung Sukarno Hatta", 407),
    1107: ("KCP METRO TRADE CENTER", 407),
    2058: ("KCP BATUNUNGGAL", 407),
    2154: ("KCP ANTAPANI", 407),
    
    # KC Bandung Setiabudi (KODE_KANCA: 408)
    408: ("KC Bandung Setiabudi", 408),
    655: ("KCP SETRASARI", 408),
    2000: ("KCP CIHAMPELAS", 408),
    2016: ("KCP LEMBANG", 408),
    
    # KC Soreang (KODE_KANCA: 544)
    544: ("KC Soreang", 544),
    1140: ("KCP BANJARAN", 544),
}

# ==================================================================================
# DAFTAR KODE KANCA (untuk filtering KANCA ONLY)
# ==================================================================================
KANCA_CODES: List[int] = list(KANCA_MASTER.keys())

# ==================================================================================
# DAFTAR KODE KCP (untuk filtering KCP ONLY)
# Semua UKER yang KODE_UKER != KODE_KANCA_INDUK
# ==================================================================================
KCP_CODES: List[int] = [
    kode_uker for kode_uker, (nama, kode_kanca) in UKER_MASTER.items()
    if kode_uker != kode_kanca and nama.upper().startswith("KCP")
]

# ==================================================================================
# HELPER FUNCTIONS
# ==================================================================================

def is_kanca(kode_uker: int) -> bool:
    """
    Check if KODE_UKER is a KANCA (Kantor Cabang)
    KANCA jika KODE_UKER ada di KANCA_MASTER
    """
    return kode_uker in KANCA_MASTER


def is_kcp(kode_uker: int) -> bool:
    """
    Check if KODE_UKER is a KCP (Kantor Cabang Pembantu)
    KCP jika KODE_UKER ada di UKER_MASTER dan bukan KANCA
    """
    if kode_uker not in UKER_MASTER:
        return False
    nama, kode_kanca = UKER_MASTER[kode_uker]
    return kode_uker != kode_kanca and nama.upper().startswith("KCP")


def get_kanca_induk(kode_uker: int) -> Optional[int]:
    """
    Get KODE_KANCA induk dari suatu KODE_UKER
    """
    if kode_uker in UKER_MASTER:
        return UKER_MASTER[kode_uker][1]
    return None


def get_uker_name(kode_uker: int) -> Optional[str]:
    """
    Get nama UKER dari KODE_UKER
    """
    if kode_uker in UKER_MASTER:
        return UKER_MASTER[kode_uker][0]
    return None


def get_kcp_by_kanca(kode_kanca: int) -> List[Tuple[int, str]]:
    """
    Get list of KCP (kode, nama) under a specific KANCA.
    Excludes any UKER codes that are also defined as KANCA to avoid double counting.
    """
    result = []
    for kode_uker, (nama, induk) in UKER_MASTER.items():
        # Only include if:
        # 1. Parent KANCA matches
        # 2. Not the KANCA itself
        # 3. Not in KANCA_CODES (to handle edge cases like 137)
        if induk == kode_kanca and kode_uker != kode_kanca and kode_uker not in KANCA_CODES:
            result.append((kode_uker, nama))
    return result


def get_uker_type(kode_uker: int) -> str:
    """
    Determine the type of UKER:
    - 'KANCA' for Kantor Cabang
    - 'KCP' for Kantor Cabang Pembantu
    - 'RO' for Regional Office
    - 'UNKNOWN' if not found
    """
    if kode_uker not in UKER_MASTER:
        return 'UNKNOWN'
    
    nama, kode_kanca = UKER_MASTER[kode_uker]
    
    if nama.upper().startswith("RO "):
        return 'RO'
    elif kode_uker == kode_kanca:
        return 'KANCA'
    elif nama.upper().startswith("KCP"):
        return 'KCP'
    else:
        return 'KANCA'  # Default to KANCA if name starts with KC


# ==================================================================================
# DJANGO QUERYSET FILTERS
# Fungsi untuk filtering queryset berdasarkan tipe UKER
# Field yang digunakan: 'kode_uker' (sesuai model LW321)
# ==================================================================================

def filter_kanca_only(queryset):
    """
    Filter queryset untuk hanya menampilkan data KANCA (Kantor Cabang)
    Asumsi: queryset memiliki field 'kode_uker' yang berisi KODE_UKER
    """
    # Convert KANCA_CODES to strings since kode_uker is CharField
    kanca_codes_str = [str(code) for code in KANCA_CODES]
    return queryset.filter(kode_uker__in=kanca_codes_str)


def filter_kcp_only(queryset):
    """
    Filter queryset untuk hanya menampilkan data KCP (Kantor Cabang Pembantu)
    Asumsi: queryset memiliki field 'kode_uker' yang berisi KODE_UKER
    """
    # Convert KCP_CODES to strings since kode_uker is CharField
    kcp_codes_str = [str(code) for code in KCP_CODES]
    return queryset.filter(kode_uker__in=kcp_codes_str)


def filter_kanca_konsol(queryset):
    """
    Filter queryset untuk KANCA KONSOL (gabungan KANCA + KCP)
    Pada dasarnya tidak ada filter, semua data ditampilkan
    """
    return queryset  # No filter, return all


# ==================================================================================
# GROUPING FOR TABLE VIEWS
# ==================================================================================

def get_kanca_with_kcp_grouped() -> Dict[int, Dict]:
    """
    Get KANCA with their KCP grouped for table display
    Returns: {
        kode_kanca: {
            'nama': 'KC Bandung AA',
            'kcp_list': [(675, 'KCP RAJAWALI BANDUNG'), ...]
        }
    }
    """
    result = {}
    for kode_kanca, nama_kanca in KANCA_MASTER.items():
        kcp_list = get_kcp_by_kanca(kode_kanca)
        result[kode_kanca] = {
            'nama': nama_kanca,
            'kcp_list': kcp_list,
        }
    return result


# ==================================================================================
# EXPORT ALL
# ==================================================================================

__all__ = [
    'KANCA_MASTER',
    'UKER_MASTER',
    'KANCA_CODES',
    'KCP_CODES',
    'is_kanca',
    'is_kcp',
    'get_kanca_induk',
    'get_uker_name',
    'get_kcp_by_kanca',
    'get_uker_type',
    'filter_kanca_only',
    'filter_kcp_only',
    'filter_kanca_konsol',
    'get_kanca_with_kcp_grouped',
]
