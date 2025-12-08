# Dashboard Formulas

This directory contains the business logic and formulas for the dashboard data processing.

## Modules

### `segmentation.py`
Contains the logic to map the `description` field to business segments (CC, SMALL, MEDIUM, KUR).
**Usage:**
```python
from dashboard.formulas import get_segment_annotation
qs = LW321.objects.annotate(segment=get_segment_annotation())
```

### `calculations.py`
Contains the logic for calculating financial metrics (OS, NPL, SML, LR, LAR).
**Usage:**
```python
from dashboard.formulas import annotate_metrics
qs = LW321.objects.all()
qs = annotate_metrics(qs)
# Now you can access qs[0].os, qs[0].npl, etc.
```

### `filters.py`
Contains helper functions for filtering data.
**Usage:**
```python
from dashboard.formulas import filter_by_period, filter_by_uker
qs = filter_by_period(qs, '2023-10-01')
qs = filter_by_uker(qs, 'JAKARTA')
```

### `utils.py`
Helper functions for data conversion and extraction.
- `cast_to_decimal`: Converts CharField numbers to Decimal.
- `extract_period_from_filename`: Extracts YYYY-MM-DD from filenames.

### `cleaning.py`
Data cleaning and standardization logic.
- `standardize_uker`: Aligns KANCA/UKER fields.

### `uker_mapping.py`
Master data dan fungsi untuk mapping KANCA (Kantor Cabang), UKER (Unit Kerja), dan KCP (Kantor Cabang Pembantu).

**Struktur Hierarki:**
- **KANCA/KC**: Kantor Cabang (level utama) - contoh: KC Bandung AA, KC Garut
- **UKER**: Unit Kerja (bisa KANCA atau KCP)
- **KCP**: Kantor Cabang Pembantu (sub-unit) - contoh: KCP RAJAWALI BANDUNG
- **RO**: Regional Office - contoh: RO BANDUNG

**Master Data:**
- `KANCA_MASTER`: Dict[kode_kanca, nama_kanca] - 31 KANCA
- `UKER_MASTER`: Dict[kode_uker, (nama_uker, kode_kanca_induk)] - 73 UKER total
- `KANCA_CODES`: List kode KANCA (31 items)
- `KCP_CODES`: List kode KCP (42 items)

**Helper Functions:**
```python
from dashboard.formulas import (
    is_kanca,              # Check if UKER is KANCA
    is_kcp,                # Check if UKER is KCP
    get_kanca_induk,       # Get parent KANCA code
    get_uker_name,         # Get UKER name from code
    get_kcp_by_kanca,      # Get list of KCP under a KANCA
    get_uker_type,         # Get type: 'KANCA', 'KCP', 'RO', 'UNKNOWN'
)
```

**Django QuerySet Filters:**
```python
from dashboard.formulas import (
    filter_kanca_only,     # Filter only KANCA records
    filter_kcp_only,       # Filter only KCP records
    filter_kanca_konsol,   # No filter (all records - KANCA + KCP)
)

# Contoh penggunaan untuk table "OS Small"
qs = LW321.objects.filter(segment='SMALL')

# TOTAL OS SMALL KANCA KONSOL (gabungan)
qs_konsol = filter_kanca_konsol(qs)

# TOTAL OS SMALL KANCA ONLY
qs_kanca = filter_kanca_only(qs)

# TOTAL OS SMALL KCP ONLY
qs_kcp = filter_kcp_only(qs)
```

**Grouping for Tables:**
```python
from dashboard.formulas import get_kanca_with_kcp_grouped

# Returns: {kode_kanca: {'nama': 'KC ...', 'kcp_list': [(kode, nama), ...]}}
grouped = get_kanca_with_kcp_grouped()
```

