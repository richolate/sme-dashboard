"""
Test _parse_periode function with various formats
"""
import os
import sys
import django
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Import after django.setup()
sys.path.insert(0, os.path.dirname(__file__))
from data_management.utils import _parse_periode

print("\n" + "="*80)
print("TEST _parse_periode FUNCTION")
print("="*80)

test_cases = [
    ('30/11/2025', '30/11/2025'),
    ('29/11/2025', '29/11/2025'),
    ('01/12/2025', '01/12/2025'),
    ('31/12/2024', '31/12/2024'),
    (pd.Timestamp('2025-11-30'), '30/11/2025'),
    ('30-11-2025', '30-11-2025'),  # Keep as-is
    ('2025-11-30', '2025-11-30'),  # Keep as-is
]

print("\nTest cases:")
all_passed = True
for input_val, expected in test_cases:
    result = _parse_periode(input_val)
    passed = result == expected
    status = "✅ PASS" if passed else "❌ FAIL"
    
    print(f"\n{status}")
    print(f"  Input:    {repr(input_val)}")
    print(f"  Expected: '{expected}'")
    print(f"  Got:      '{result}'")
    
    if not passed:
        all_passed = False

print("\n" + "="*80)
if all_passed:
    print("✅ ALL TESTS PASSED!")
else:
    print("❌ SOME TESTS FAILED")
print("="*80 + "\n")
