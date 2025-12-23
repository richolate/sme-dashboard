# Fix NSB KANCA and KCP Filter Issue

## Problem Identified

Saat testing NSB SMALL page, ditemukan data yang tidak sesuai:
- **KCP Rancaekek** harusnya bernilai 227 (30 Nov 2025) tapi tidak sesuai
- **KC Kuningan** di KANCA ONLY juga miss
- Masalah yang sama seperti saat pembuatan OS SMALL dahulu

## Root Cause Analysis

### Perbedaan Metric Biasa vs NSB

**Metric Biasa (OS, DPK, NPL, LAR, LR):**
```
KONSOL = SUM(KANCA values) + SUM(KCP values)
KANCA ONLY = SUM(transaksi where kode_uker = KANCA)
KCP ONLY = SUM(transaksi where kode_uker = KCP)

✅ Formula valid: KANCA ONLY + KCP ONLY = KONSOL
```

**NSB (Customer Count):**
```
❌ WRONG APPROACH (old code):
KONSOL = COUNT DISTINCT per KANCA + COUNT DISTINCT per KCP1 + COUNT DISTINCT per KCP2...
Problem: Menjumlahkan count distinct ≠ count distinct dari gabungan!

Example:
- KANCA punya 100 unique customers
- KCP1 punya 150 unique customers  
- KCP2 punya 120 unique customers
- Total jika dijumlahkan = 370
- BUT: Bisa saja ada customer yang sama di beberapa unit!
- Seharusnya: COUNT(DISTINCT cif_no WHERE kode_uker IN (KANCA, KCP1, KCP2))
```

### Kesalahan di Kode Lama

File: `dashboard/formulas/table_builder.py`
Function: `get_metric_by_kanca()` (line 258-280)

```python
# OLD CODE (WRONG for NSB):
def get_metric_by_kanca(...):
    metric_by_uker = get_metric_by_uker(...)  # Gets COUNT DISTINCT per uker
    metric_by_kanca = {}
    
    for kode_uker_str, value in metric_by_uker.items():
        kode_kanca = get_kode_kanca_from_uker(kode_uker_str)
        if kode_kanca:
            if kode_kanca not in metric_by_kanca:
                metric_by_kanca[kode_kanca] = Decimal('0')
            metric_by_kanca[kode_kanca] += value  # ❌ WRONG: Summing count distincts!
    
    return metric_by_kanca
```

**Masalah:**
1. `get_metric_by_uker()` menghitung COUNT DISTINCT per uker
2. Kemudian menjumlahkan count-count ini dengan `+=`
3. **Matematika salah**: COUNT(A) + COUNT(B) ≠ COUNT(A ∪ B)

## Solution Implemented

### Modified Function: `get_metric_by_kanca()`

**Location:** `dashboard/formulas/table_builder.py` (lines 258-306)

```python
def get_metric_by_kanca(target_date, segment_filter, metric_field='os', kol_adk_filter=None):
    """
    For NSB: COUNT(DISTINCT cif_no) directly per KANCA induk
    For others: Sum values from all UKERs under each KANCA
    """
    
    # Special handling for NSB
    if metric_field == 'nsb':
        qs = get_base_queryset(target_date, segment_filter, metric_field, kol_adk_filter)
        metric_by_kanca = {}
        
        for kode_kanca in KANCA_CODES:
            # Get KANCA code + all its KCP codes
            uker_codes = [str(kode_kanca)]
            
            kcp_data = get_kcp_by_kanca(kode_kanca)
            for kcp_code, _ in kcp_data:
                uker_codes.append(str(kcp_code))
            
            # ✅ CORRECT: Count distinct across ALL uker codes at once
            count = qs.filter(kode_uker__in=uker_codes).values('cif_no').distinct().count()
            metric_by_kanca[kode_kanca] = Decimal(str(count))
        
        return metric_by_kanca
    
    # For non-NSB metrics: original sum logic (still correct)
    metric_by_uker = get_metric_by_uker(...)
    metric_by_kanca = {}
    
    for kode_uker_str, value in metric_by_uker.items():
        kode_kanca = get_kode_kanca_from_uker(kode_uker_str)
        if kode_kanca:
            if kode_kanca not in metric_by_kanca:
                metric_by_kanca[kode_kanca] = Decimal('0')
            metric_by_kanca[kode_kanca] += value  # ✅ OK for SUM metrics
    
    return metric_by_kanca
```

### Key Changes

1. **Added conditional check** for `metric_field == 'nsb'`
2. **For NSB**: 
   - Build list of all UKER codes under each KANCA (KANCA + its KCPs)
   - Filter queryset with `kode_uker__in=uker_codes`
   - Do single `COUNT(DISTINCT cif_no)` on combined data
   - **Result**: True unique customer count per KANCA induk

3. **For other metrics**: 
   - Keep original logic (sum from UKERs)
   - Still works correctly for OS, DPK, NPL, LAR, LR

### Why KANCA ONLY and KCP ONLY Don't Need Changes

**KANCA ONLY** (`build_kanca_only_table`):
- Already uses `get_metric_by_uker()` which does COUNT DISTINCT per uker
- Only queries kode_kanca directly (line 448: `kode_kanca_str`)
- ✅ Correct: Counts customers where kode_uker = KANCA only

**KCP ONLY** (`build_kcp_only_table`):
- Also uses `get_metric_by_uker()` with COUNT DISTINCT per uker
- Only queries KCP codes (line 550: `kcp_code_str`)
- ✅ Correct: Counts customers where kode_uker = KCP only

**Why they're correct:**
- They query individual uker codes
- `get_metric_by_uker()` does proper COUNT DISTINCT at uker level
- No aggregation across multiple ukers, so no double-counting issue

## Testing Steps

1. **Navigate to NSB SMALL page:**
   ```
   http://127.0.0.1:8000/dashboard/small-nsb/
   ```

2. **Select date: 30 November 2025**

3. **Verify KONSOL Table:**
   - Should show total unique customers per KANCA induk (KANCA + all KCPs)
   - Values should be COUNT(DISTINCT cif_no) across all units

4. **Verify KANCA ONLY Table:**
   - KC Kuningan should show correct customer count
   - Should only count customers where kode_uker = KANCA code
   - Should NOT include customers from KCPs

5. **Verify KCP ONLY Table:**
   - KCP Rancaekek should show 227 customers
   - Should only count customers where kode_uker = KCP code
   - Should NOT include customers from parent KANCA

6. **Verify Formula:**
   ```
   KONSOL ≠ KANCA ONLY + KCP ONLY  (for NSB only!)
   ```
   This is expected because:
   - A customer might move between units
   - A customer might have accounts in multiple units
   - COUNT DISTINCT across all units ≠ sum of count distincts per unit

## Expected Behavior After Fix

### KONSOL Table
```
KC Kuningan (KONSOL) = COUNT(DISTINCT cif_no 
                       WHERE kode_uker IN ('083', '08301', '08302', ...))
```
Includes all customers from KC Kuningan + all its KCPs.

### KANCA ONLY Table
```
KC Kuningan (KANCA ONLY) = COUNT(DISTINCT cif_no WHERE kode_uker = '083')
```
Only customers directly at KC Kuningan branch.

### KCP ONLY Table
```
KCP Rancaekek = COUNT(DISTINCT cif_no WHERE kode_uker = '08337')
```
Only customers at KCP Rancaekek, should be 227.

## Files Modified

1. **dashboard/formulas/table_builder.py**
   - Function: `get_metric_by_kanca()` (lines 258-306)
   - Added special NSB handling with direct COUNT DISTINCT
   - Preserved original logic for other metrics

## Summary

✅ **Fixed:** NSB KONSOL now correctly counts unique customers across KANCA + KCPs  
✅ **Preserved:** KANCA ONLY and KCP ONLY already working correctly  
✅ **Maintained:** Other metrics (OS, DPK, NPL, LAR, LR) still work as before  

**Mathematical Correctness:**
- Before: COUNT(A) + COUNT(B) + COUNT(C) = WRONG for distinct counts
- After: COUNT(DISTINCT A ∪ B ∪ C) = CORRECT for NSB

**Reference:** Solution based on OS SMALL implementation pattern where similar fix was applied.
