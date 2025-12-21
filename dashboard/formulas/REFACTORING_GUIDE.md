# Refactoring Guide: Modular Table Building System

## Overview
The table building logic has been extracted from `views.py` into reusable modules to prevent code duplication across 40+ metric pages.

## New Module Files

### 1. `dashboard/formulas/table_builder.py`
**Purpose:** Core table building logic  
**Status:** ✅ COMPLETE

**Key Functions:**
- `get_date_columns(selected_date)` - Calculate columns A, B, C, D, E dates
- `get_metric_by_uker(target_date, segment_filter, metric_field)` - Get metrics by UKER code
- `get_metric_by_kanca(target_date, segment_filter, metric_field)` - Get metrics by KANCA (with KCP consolidation)
- `calculate_changes(A, B, C, D, E)` - Calculate DtD, MoM, MtD, YtD with percentages
- `build_konsol_table(date_columns, segment_filter, metric_field)` - Build KONSOL table (30 KANCAs)
- `build_kanca_only_table(date_columns, segment_filter, metric_field)` - Build KANCA ONLY table
- `build_kcp_only_table(date_columns, segment_filter, metric_field)` - Build KCP ONLY table
- `build_metric_tables(selected_date, segment_filter, metric_field)` - Main entry point

**Supported Metrics:**
- `'os'` - Outstanding
- `'dpk'` - Dana Pihak Ketiga (mapped to 'sml' field)
- `'dpk_pct'` - %DPK = (sml / os) * 100
- `'npl'` - Non-Performing Loan
- `'npl_pct'` - %NPL = (npl / os) * 100
- `'lar'` - Loan at Risk
- `'lr'` - Loan Restructured
- `'nsb'` - Nasabah count (customer count)

**Percentage Metrics Logic:**
```python
# %DPK = (DPK / OS) * 100
# %NPL = (NPL / OS) * 100
# Calculated at UKER level, then aggregated
```

### 2. `dashboard/formulas/metric_handlers.py`
**Purpose:** View handler functions for each metric type  
**Status:** ✅ COMPLETE

**Available Handlers:**
- `handle_os_view(request, segment_filter)` - OS metric
- `handle_dpk_view(request, segment_filter)` - DPK metric
- `handle_dpk_pct_view(request, segment_filter)` - %DPK metric
- `handle_npl_view(request, segment_filter)` - NPL metric
- `handle_npl_pct_view(request, segment_filter)` - %NPL metric
- `handle_lar_view(request, segment_filter)` - LAR metric
- `handle_nsb_view(request, segment_filter)` - NSB metric
- `handle_lr_view(request, segment_filter)` - LR metric
- `get_metric_handler(metric_type)` - Helper to get handler by name

**Handler Structure:**
Each handler:
1. Parses selected_date from request.GET
2. Calls `build_metric_tables(date, segment, metric_field)`
3. Returns context dict with tables data

## How to Update views.py

### Before (370+ lines per metric):
```python
def small_os(request):
    # 1. Parse date (20 lines)
    # 2. Calculate date columns A-E (50 lines)
    # 3. Build KONSOL table (100 lines)
    # 4. Build KANCA ONLY table (100 lines)
    # 5. Build KCP ONLY table (100 lines)
    # 6. Prepare context (50 lines)
    # Total: ~370 lines
    return render(request, 'dashboard/metric_page.html', context)
```

### After (15-20 lines per metric):
```python
from .formulas.metric_handlers import handle_os_view

def small_os(request):
    """OS SMALL - Outstanding balance for SMALL segment."""
    context = handle_os_view(request, segment_filter='SMALL')
    return render(request, 'dashboard/metric_page.html', context)

def medium_os(request):
    """OS MEDIUM - Outstanding balance for MEDIUM segment."""
    context = handle_os_view(request, segment_filter='MEDIUM')
    return render(request, 'dashboard/metric_page.html', context)

def small_dpk(request):
    """DPK SMALL - Dana Pihak Ketiga for SMALL segment."""
    context = handle_dpk_view(request, segment_filter='SMALL')
    return render(request, 'dashboard/metric_page.html', context)

def small_dpk_pct(request):
    """%DPK SMALL - Percentage DPK to OS for SMALL segment."""
    context = handle_dpk_pct_view(request, segment_filter='SMALL')
    return render(request, 'dashboard/metric_page.html', context)

def small_npl_pct(request):
    """%NPL SMALL - NPL ratio for SMALL segment."""
    context = handle_npl_pct_view(request, segment_filter='SMALL')
    return render(request, 'dashboard/metric_page.html', context)
```

### Code Reduction:
- **From:** 370 lines × 8 SMALL metrics = 2,960 lines
- **To:** 20 lines × 8 SMALL metrics = 160 lines
- **Savings:** ~2,800 lines (95% reduction)

## Menu Structure & Required View Functions

### MEDIUM Section (8 views):
```python
def medium_os(request):
    return render(request, 'dashboard/metric_page.html', 
                  handle_os_view(request, 'MEDIUM'))

def medium_dpk(request):
    return render(request, 'dashboard/metric_page.html', 
                  handle_dpk_view(request, 'MEDIUM'))

def medium_dpk_pct(request):
    return render(request, 'dashboard/metric_page.html', 
                  handle_dpk_pct_view(request, 'MEDIUM'))

def medium_npl(request):
    return render(request, 'dashboard/metric_page.html', 
                  handle_npl_view(request, 'MEDIUM'))

def medium_lar(request):
    return render(request, 'dashboard/metric_page.html', 
                  handle_lar_view(request, 'MEDIUM'))

def medium_nsb(request):
    return render(request, 'dashboard/metric_page.html', 
                  handle_nsb_view(request, 'MEDIUM'))

def medium_lr(request):
    return render(request, 'dashboard/metric_page.html', 
                  handle_lr_view(request, 'MEDIUM'))
```

### SMALL Section (8 views):
```python
def small_os(request): ...      # Already exists - needs refactoring
def small_dpk(request): ...     # New
def small_dpk_pct(request): ... # New
def small_npl(request): ...     # New
def small_npl_pct(request): ... # New
def small_lar(request): ...     # New
def small_nsb(request): ...     # New
def small_lr(request): ...      # New
```

### SMALL NCC Section (8 views):
```python
def small_ncc_os(request):
    return render(request, 'dashboard/metric_page.html', 
                  handle_os_view(request, 'SMALL NCC'))

def small_ncc_dpk(request):
    return render(request, 'dashboard/metric_page.html', 
                  handle_dpk_view(request, 'SMALL NCC'))

# ... etc for dpk-pct, npl, npl-pct, lar, nsb, lr
```

### CC Section (8 views):
```python
def cc_os(request):
    return render(request, 'dashboard/metric_page.html', 
                  handle_os_view(request, 'CC'))

# ... etc for dpk, dpk-pct, npl, npl-pct, lar, nsb, lr
```

### KUR Section (8 views):
```python
def kur_os(request):
    return render(request, 'dashboard/metric_page.html', 
                  handle_os_view(request, 'KUR'))

# ... etc for dpk, dpk-pct, npl, npl-pct, lar, nsb, lr
```

## Total View Functions Needed

| Section    | Metrics | Total Views |
|------------|---------|-------------|
| MEDIUM     | 8       | 8           |
| SMALL      | 8       | 8           |
| SMALL NCC  | 8       | 8           |
| CC         | 8       | 8           |
| KUR        | 8       | 8           |
| **TOTAL**  | **40**  | **40**      |

**Lines of code:**
- Old approach: 370 lines × 40 = **14,800 lines**
- New approach: 20 lines × 40 = **800 lines**
- **Savings: 14,000 lines (95% reduction)**

## Next Steps

### 1. Refactor existing `small_os` view
- Location: `dashboard/views.py` line ~1007-1375
- Replace 370 lines with handler call
- Test that output matches exactly

### 2. Add new view functions
Create 39 new view functions for:
- 7 new SMALL views (dpk, dpk-pct, npl, npl-pct, lar, nsb, lr)
- 8 MEDIUM views
- 8 SMALL NCC views
- 8 CC views
- 8 KUR views

### 3. Update URLs
Add URL patterns in `dashboard/urls.py`:
```python
# SMALL
path('small-dpk/', views.small_dpk, name='small-dpk'),
path('small-dpk-pct/', views.small_dpk_pct, name='small-dpk-pct'),
path('small-npl-pct/', views.small_npl_pct, name='small-npl-pct'),
# ... etc

# MEDIUM
path('medium-os/', views.medium_os, name='medium-os'),
path('medium-dpk/', views.medium_dpk, name='medium-dpk'),
# ... etc
```

### 4. Testing Checklist
- [ ] KONSOL table totals match original implementation
- [ ] KANCA ONLY table excludes KCP contributions correctly
- [ ] KCP ONLY table groups by parent KANCA correctly
- [ ] Date columns A-E calculate correctly
- [ ] DtD, MoM, MtD, YtD changes calculate correctly
- [ ] Percentage changes calculate correctly
- [ ] Number formatting displays correctly (divide by 1M)
- [ ] %DPK calculation: (dpk/os)*100 is correct
- [ ] %NPL calculation: (npl/os)*100 is correct
- [ ] Date picker updates tables correctly
- [ ] All 40 menu items link to correct views

## Benefits of Refactoring

✅ **95% code reduction** (14,800 → 800 lines)  
✅ **Single source of truth** - fixes apply to all pages  
✅ **Easy to add new metrics** - just add handler + view  
✅ **Consistent calculations** - no copy-paste errors  
✅ **Better maintainability** - changes in one place  
✅ **Faster development** - new pages in minutes  

## File Structure

```
dashboard/
├── views.py (simplified, 800 lines instead of 14,800)
├── urls.py (add 39 new URL patterns)
├── formulas/
│   ├── table_builder.py ✅ COMPLETE
│   ├── metric_handlers.py ✅ COMPLETE
│   ├── calculations.py (unchanged - provides annotate_metrics)
│   ├── segmentation.py (unchanged - provides segment annotation)
│   └── ...
```

## Example: Adding a New Metric

If you need to add a new metric in the future (e.g., "CKPN"):

1. **Add calculation to `calculations.py`:**
```python
def annotate_metrics(queryset):
    return queryset.annotate(
        # ... existing metrics
        ckpn=Sum('some_field')  # Add new metric
    )
```

2. **Add handler to `metric_handlers.py`:**
```python
def handle_ckpn_view(request, segment_filter='SMALL'):
    # ... same structure as other handlers
    table_data = build_metric_tables(
        selected_date=selected_date,
        segment_filter=segment_filter,
        metric_field='ckpn'  # Use new field
    )
    return context
```

3. **Add views to `views.py`:**
```python
def small_ckpn(request):
    return render(request, 'dashboard/metric_page.html',
                  handle_ckpn_view(request, 'SMALL'))

def medium_ckpn(request):
    return render(request, 'dashboard/metric_page.html',
                  handle_ckpn_view(request, 'MEDIUM'))
# ... etc for all segments
```

4. **Add URLs and menu items** - Done!

**Total time: ~30 minutes instead of days of copy-pasting!**
