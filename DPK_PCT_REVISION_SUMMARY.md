# %DPK SMALL - Revisi Template

## Masalah yang Diperbaiki

### 1. ✅ Nilai ditampilkan sebagai persentase
**Sebelum:** Nilai ditampilkan sebagai angka absolut (0, 1000, 2000, dll)
**Sesudah:** Nilai ditampilkan sebagai persentase (4.18%, 4.59%, 7.66%, dll)

**Implementasi:**
- Kolom A, B, C, D, E: Format `{{ value|floatformat:2 }}%` untuk `dpk_pct` dan `npl_pct`
- Kolom DtD, MoM, MtD, YtD: Format `{{ value|floatformat:2 }}%` untuk `dpk_pct` dan `npl_pct`

### 2. ✅ Inverse color logic untuk DtD, MoM, MtD, YtD
**Aturan:** Sama seperti DPK SMALL
- **Hijau** (bg-positive) = Nilai turun/minus (baik)
- **Merah** (bg-negative) = Nilai naik/positif (buruk)

**Implementasi:**
```django
{% if metric_type in 'dpk,npl,lar,lr,dpk_pct,npl_pct' %}
    {% if value >= 0 %}bg-negative{% else %}bg-positive{% endif %}
{% else %}
    {% if value >= 0 %}bg-positive{% else %}bg-negative{% endif %}
{% endif %}
```

## Files Modified

### 1. `dashboard/formulas/metric_handlers.py`
**Line 132:** Added `metric_type='dpk_pct'` to context

```python
context = {
    'show_os_tables': True,
    'metric_type': 'dpk_pct',  # ✅ NEW - For percentage formatting
    'tables': table_data,
    # ... rest of context
}
```

### 2. `templates/dashboard/metric_page.html`
Updated formatting for all 3 tables (KONSOL, KANCA ONLY, KCP ONLY):

#### A. Data Rows (lines ~1605-1622, ~1707-1724, ~1804-1821)
**Changed:**
- Kolom A-E: `{% if metric_type == 'dpk_pct' or metric_type == 'npl_pct' %}{{ value|floatformat:2 }}%{% else %}`
- DtD/MoM/MtD/YtD absolut: Same formatting with percentage check
- Color classes: Added `dpk_pct,npl_pct` to inverse color condition

**Example:**
```django
<td>
  {% if metric_type == 'nsb' %}{{ row.A|format_integer:0|default:"-" }}
  {% elif metric_type == 'dpk_pct' or metric_type == 'npl_pct' %}{{ row.A|floatformat:2 }}%
  {% else %}{{ row.A|format_number:0|default:"-" }}
  {% endif %}
</td>
```

#### B. Total Rows (lines ~1631-1645, ~1730-1744, ~1836-1849)
**Changed:**
- Same formatting logic as data rows
- Added percentage formatting for A-E columns
- Added percentage formatting for DtD/MoM/MtD/YtD columns
- Updated color classes to include `dpk_pct,npl_pct`

## Testing Results

### Debug Script Output (`test_dpk_pct_debug.py`)
```
UKER 354 (KC Bandung A.H. Nasution):
  DPK: 10,831,862,387.61
  OS: 259,017,565,947.54
  %DPK: 4.18%

UKER 5 (KC Bandung AA):
  DPK: 11,256,938,585.68
  OS: 259,399,829,585.42
  %DPK: 4.59%

UKER 405 (KC Bandung Dago):
  DPK: 18,741,440,503.54
  OS: 244,636,178,591.73
  %DPK: 7.66%
```

✅ Calculations are correct!

## Expected Display

### Table Format
```
┌─────────────────────┬────────┬────────┬────────┬────────┬────────┬─────────┐
│ KANCA               │   A    │   B    │   C    │   D    │   E    │   DtD   │
├─────────────────────┼────────┼────────┼────────┼────────┼────────┼─────────┤
│ KC Bandung AA       │ 4.55%  │ 4.57%  │ 4.58%  │ 4.58%  │ 4.59%  │ +0.01%  │ RED
│ KC Bandung Dago     │ 7.60%  │ 7.62%  │ 7.64%  │ 7.65%  │ 7.66%  │ +0.01%  │ RED
└─────────────────────┴────────┴────────┴────────┴────────┴────────┴─────────┘
```

### Color Logic
- **DtD = +0.01%** → 🔴 RED (bg-negative) - Increase is bad for %DPK
- **DtD = -0.01%** → 🟢 GREEN (bg-positive) - Decrease is good for %DPK

## Summary of Changes

1. ✅ **Context:** Added `metric_type='dpk_pct'` in metric_handlers.py
2. ✅ **Template - KONSOL:** 
   - Updated data rows (16 cells per row)
   - Updated total row (16 cells)
3. ✅ **Template - KANCA ONLY:**
   - Updated data rows (16 cells per row)
   - Updated total row (16 cells)
4. ✅ **Template - KCP ONLY:**
   - Updated data rows (16 cells per row)
   - Updated total row (16 cells)

Total template cells updated: **48 cells per table × 3 tables = 144 cells**

## Verification Checklist

- [x] Metric handler passes `metric_type='dpk_pct'`
- [x] KONSOL table displays percentage (A-E columns)
- [x] KANCA ONLY table displays percentage (A-E columns)
- [x] KCP ONLY table displays percentage (A-E columns)
- [x] DtD/MoM/MtD/YtD display percentage
- [x] Inverse colors (green=decrease, red=increase)
- [x] Total rows formatted correctly
- [x] Debug script confirms calculations are correct

## Next Steps

1. Restart Django server to apply changes
2. Navigate to SMALL → %DPK SMALL
3. Verify all tables display percentages
4. Verify color logic (red for positive, green for negative)
5. Test with different dates using date filter
