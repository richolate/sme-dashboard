"""
Test date string parsing
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import pandas as pd
from data_management.utils import _parse_date_string

# Test cases
test_dates = [
    '2026-02-08',  # YYYY-MM-DD format
    '02/08/2026',  # MM/DD/YYYY format (should preserve)
    '2017-04-10',  # YYYY-MM-DD
    '04/10/2017',  # MM/DD/YYYY
    '0',           # Zero string
    0,             # Zero number
    '',            # Empty string
    None,          # None
    pd.Timestamp('2025-12-25'),  # Pandas timestamp
]

print("=" * 70)
print("DATE STRING PARSING TEST")
print("=" * 70)

for test_value in test_dates:
    result = _parse_date_string(test_value)
    print(f"Input: {repr(test_value):30} → Output: '{result}'")

print("\n" + "=" * 70)
