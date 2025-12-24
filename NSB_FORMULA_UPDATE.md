# NSB Formula Update - December 24, 2025

## Summary
Updated NSB (Nasabah) calculation formula from counting distinct CIF numbers to summing NASABAH column where DUB_NASABAH='TRUE'.

## Previous Formula
```python
NSB = COUNT(DISTINCT CIF_NO) WHERE segment=SMALL
```

## New Formula
```python
NSB = SUM(NASABAH) WHERE segment=SMALL AND DUB_NASABAH='TRUE'
```

## Rationale
- More accurate customer counting by using dedicated NASABAH column
- DUB_NASABAH='TRUE' filter ensures only unique/deduplicated customers are counted
- Each record stores actual customer count in NASABAH field (e.g., 1, 2, 3)
- Allows aggregation by KC/KCP to show how many customers each branch has

## Files Modified

### 1. `dashboard/formulas/calculations.py`
**Function:** `count_unique_customers()`

**Changes:**
- Updated docstring to reflect new formula
- Changed from `Count('cif_no', distinct=True)` to `Sum('nasabah')`
- Added filter for `dub_nasabah='TRUE'`
- Returns sum instead of count

```python
def count_unique_customers(queryset, segment='SMALL'):
    """
    Counts total customers by summing NASABAH column for a given segment.
    This is used for NSB (Nasabah/Customer count) metric.
    
    FORMULA: SUM(NASABAH) WHERE segment=SMALL AND DUB_NASABAH='TRUE'
    """
    from .segmentation import get_segment_annotation
    
    # Annotate with segment
    qs = queryset.annotate(segment=get_segment_annotation())
    
    # Filter by segment and DUB_NASABAH = 'TRUE'
    qs = qs.filter(segment=segment, dub_nasabah='TRUE')
    
    # Sum NASABAH column (handle NULL values)
    result = qs.aggregate(total_nasabah=Sum('nasabah'))
    
    # Return 0 if NULL
    return result['total_nasabah'] or 0
```

### 2. `dashboard/formulas/table_builder.py`
**Function:** `get_metric_by_uker()`

**Changes:**
- Updated NSB handling logic
- Changed from `Count('cif_no', distinct=True)` to `Sum('nasabah')`
- Added filter for `dub_nasabah='TRUE'`
- Updated docstring

```python
# Handle NSB (customer count) specially
if metric_field == 'nsb':
    # Sum NASABAH column per UKER where DUB_NASABAH='TRUE'
    result = qs.filter(dub_nasabah='TRUE').values('kode_uker').annotate(
        total=Sum('nasabah')
    ).order_by('kode_uker')
    
    # Convert to Decimal for consistency with other metrics
    return {item['kode_uker']: Decimal(str(item['total'] or 0)) for item in result}
```

## Testing

### Test Script
Created `test_nsb_nasabah_sum.py` to verify:
1. Manual query calculation
2. Function result matches manual calculation
3. Breakdown by UKER

### Run Test
```bash
python test_nsb_nasabah_sum.py
```

## Data Requirements

### Excel File Columns
1. **NASABAH** (numeric)
   - Contains customer count per record
   - Example values: 1, 2, 3
   - Should not be empty or 'None' string

2. **DUB NASABAH** (VARCHAR(10))
   - Contains 'TRUE' or 'FALSE' string
   - 'TRUE' = unique/deduplicated customer
   - 'FALSE' = duplicate customer record
   - Filter by 'TRUE' to avoid double-counting

### Database Fields
```python
# dashboard/models.py - LW321 model
nasabah = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
dub_nasabah = models.CharField(max_length=10, null=True, blank=True)
```

## Impact

### Views Affected
- NSB SMALL view (`/dashboard/nsb-small/`)
- NSB MEDIUM view (`/dashboard/nsb-medium/`)
- NSB COMMERCIAL view (`/dashboard/nsb-commercial/`)

### Table Display
- **By UKER:** Shows SUM(NASABAH) per branch office
- **By KANCA:** Aggregates NASABAH from all UKERs under each KANCA
- **Konsolidasi:** Total of all NASABAH for the segment

### Example Output
```
KANCA 001 - KC BANDUNG
├─ KCP CICADAS      : 150 customers
├─ KCP SOREANG      : 200 customers
└─ Total KC BANDUNG : 350 customers
```

## Migration Path

### Step 1: Ensure Data Uploaded
- Upload Excel file with NASABAH and DUB NASABAH columns populated
- Verify NASABAH contains numeric values (not 'None' string)
- Verify DUB_NASABAH contains 'TRUE' or 'FALSE'

### Step 2: Restart Services
```bash
# Restart Celery worker (for upload processing)
celery -A config worker --loglevel=info --pool=solo

# Restart Django server (for web views)
python manage.py runserver
```

### Step 3: Verify Results
```bash
# Run test script
python test_nsb_nasabah_sum.py

# Check uploaded data
python check_upload_latest.py
```

## Notes
- Backward compatible: Existing code structure maintained
- Uses same `count_unique_customers()` function name
- KANCA aggregation logic unchanged (sums UKER values)
- No database migrations needed (columns already exist)

## Related Files
- `dashboard/models.py` - LW321 model definition
- `data_management/utils.py` - Upload parsing with DECIMAL_FIELDS
- `dashboard/formulas/metric_handlers.py` - NSB view handler
- `NSB_COMPLETION_SUMMARY.md` - Previous NSB implementation notes
