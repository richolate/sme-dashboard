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
