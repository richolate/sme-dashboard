# %DPK SMALL Implementation

## Overview
Halaman %DPK SMALL menampilkan persentase DPK terhadap OS dengan struktur tabel yang sama seperti OS SMALL (KONSOL, KANCA ONLY, KCP ONLY).

## Formula
```
%DPK = (DPK / OS) × 100
```

### Contoh Perhitungan
KC Bandung AA:
- DPK: 17,914
- OS: 283,753
- %DPK = (17,914 / 283,753) × 100 = 6.31%

## Implementation Details

### 1. Navigation (`dashboard/navigation.py`)
✅ Already configured:
- Slug: `small-dpk-pct`
- Title: `%DPK SMALL`
- Tables: 
  - TOTAL %DPK SMALL KANCA KONSOL
  - TOTAL %DPK SMALL KANCA ONLY
  - TOTAL %DPK SMALL KCP ONLY

### 2. URL Routing (`dashboard/urls.py`)
✅ Already configured:
- Uses generic `path('page/<slug:slug>/', views.metric_page_view)`
- Slug `small-dpk-pct` handled by `metric_page_view`

### 3. View Handler (`dashboard/views.py`)
✅ **NEW - Added:**
```python
elif slug == 'small-dpk-pct':
    from .formulas.metric_handlers import handle_dpk_pct_view
    context.update(handle_dpk_pct_view(request, segment_filter='SMALL'))
```

### 4. Metric Handler (`dashboard/formulas/metric_handlers.py`)
✅ Already exists:
- Function: `handle_dpk_pct_view(request, segment_filter='SMALL')`
- Calls: `build_metric_tables(metric_field='dpk_pct')`
- Context includes: date columns, headers for DtD/MoM/MtD/YtD

### 5. Table Builder (`dashboard/formulas/table_builder.py`)
✅ **UPDATED:**
```python
elif metric_field == 'dpk_pct':
    # %DPK = (sml / os) * 100
    # SML is already annotated in calculations.py as DPK where kol_adk='2'
    result = qs.values('kode_uker').annotate(
        metric_sum=Sum('sml'),
        base_sum=Sum('os')
    ).order_by('kode_uker')
    
    return {
        item['kode_uker']: calculate_percentage_metric(
            item['metric_sum'] or 0, 
            item['base_sum'] or 0
        ) 
        for item in result
    }
```

**Key Changes:**
- Changed from `Sum('val_dpk')` to `Sum('sml')`
- Ensures consistency with DPK SMALL page values
- Uses `sml` field which filters `kol_adk='2'` (calculated in `calculations.py`)

### 6. Calculations (`dashboard/formulas/calculations.py`)
✅ Already configured:
- Field `sml` contains DPK values (kol_adk='2')
- Formula: `SML = OS WHERE kol_adk='2'` or fallback to `val_dpk`

### 7. Percentage Calculation (`dashboard/formulas/table_builder.py`)
✅ Already exists:
```python
def calculate_percentage_metric(metric_value, base_value):
    if base_value == 0 or base_value is None:
        return 0
    if metric_value is None:
        return 0
    return (metric_value / base_value) * 100
```

## Data Flow

1. **User navigates** to `/page/small-dpk-pct/`
2. **View dispatcher** (`metric_page_view`) calls `handle_dpk_pct_view`
3. **Metric handler** calls `build_metric_tables(metric_field='dpk_pct')`
4. **Table builder** calls `get_metric_by_uker(metric_field='dpk_pct')`
5. **Query builder** aggregates:
   - `metric_sum = Sum('sml')` - Total DPK per UKER
   - `base_sum = Sum('os')` - Total OS per UKER
6. **Percentage calculation**: `(metric_sum / base_sum) * 100`
7. **Table construction**: KONSOL, KANCA ONLY, KCP ONLY with 5 date columns (A-E)
8. **Template rendering**: `dashboard/metric_page.html` with percentage formatting

## Table Structure

### Same as OS SMALL:
```
┌─────────────────┬────────┬────────┬────────┬────────┬────────┬────────┐
│ KANCA/KCP       │   A    │   B    │   C    │   D    │   E    │  DtD   │
│                 │ (Dec)  │ (1mo)  │ (EOM)  │ (H-1)  │ (Now)  │ (%)    │
├─────────────────┼────────┼────────┼────────┼────────┼────────┼────────┤
│ KC Bandung AA   │  6.25% │  6.18% │  6.20% │  6.28% │  6.31% │ +0.03% │
│ KC Jakarta BB   │  5.80% │  5.85% │  5.90% │  5.95% │  6.00% │ +0.05% │
└─────────────────┴────────┴────────┴────────┴────────┴────────┴────────┘
```

### Three Tables:
1. **KONSOL** - All KANCA with their KCP children (hierarchical)
2. **KANCA ONLY** - Only parent KANCA data (excluding KCP)
3. **KCP ONLY** - Only KCP data (excluding parent KANCA)

## Testing Checklist

- [ ] Navigate to menu "SMALL" → "%DPK SMALL"
- [ ] Verify 3 tables display correctly (KONSOL, KANCA ONLY, KCP ONLY)
- [ ] Verify date columns (A, B, C, D, E) display correct dates
- [ ] Verify percentage values calculated correctly (DPK/OS × 100)
- [ ] Test date filter (change selected date and reload)
- [ ] Verify DtD, MoM, MtD, YtD calculations
- [ ] Check KC Bandung AA: DPK=17,914, OS=283,753 → %DPK=6.31%
- [ ] Verify totals row calculates correctly

## Notes

- **Percentage Format**: Display as `6.31%` (2 decimal places)
- **Inverse Colors**: For %DPK, lower is better (like NPL)
  - Green for decrease (good)
  - Red for increase (bad)
- **Zero Division**: Returns 0% if OS = 0
- **NULL Handling**: Treats NULL as 0 in calculations

## Files Modified

1. ✅ `dashboard/views.py` - Added route for `small-dpk-pct`
2. ✅ `dashboard/formulas/table_builder.py` - Fixed DPK percentage calculation to use `sml` field
3. ✅ `dashboard/formulas/metric_handlers.py` - Already has `handle_dpk_pct_view`
4. ✅ `dashboard/navigation.py` - Already has menu configuration

## Related Pages

- **DPK SMALL** (`small-dpk`) - Shows absolute DPK values
- **%NPL SMALL** (`small-npl-pct`) - Similar percentage calculation
- **OS SMALL** (`small-os`) - Base OS values used in denominator
