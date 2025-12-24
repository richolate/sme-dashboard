"""
Check periode format and available dates in database
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from dashboard.models import LW321
from django.db.models import Count
from datetime import datetime, date

print("\n" + "="*80)
print("PERIODE FORMAT CHECK")
print("="*80)

# Get all unique periode values
periodes = LW321.objects.values('periode').annotate(
    count=Count('id')
).order_by('-periode')[:10]

print("\nTop 10 periode values in database:")
for p in periodes:
    print(f"  '{p['periode']}': {p['count']} records")

# Check specific dates
print("\n" + "="*80)
print("SPECIFIC DATE CHECKS:")
print("="*80)

# Format that get_date_columns uses
nov30_date = date(2025, 11, 30)
nov29_date = date(2025, 11, 29)

# Expected format: 30-Nov-25
expected_nov30 = nov30_date.strftime("%d-%b-%y")
expected_nov29 = nov29_date.strftime("%d-%b-%y")

print(f"\nExpected format for Nov 30, 2025: '{expected_nov30}'")
count_nov30 = LW321.objects.filter(periode=expected_nov30).count()
print(f"Records found: {count_nov30}")

print(f"\nExpected format for Nov 29, 2025: '{expected_nov29}'")
count_nov29 = LW321.objects.filter(periode=expected_nov29).count()
print(f"Records found: {count_nov29}")

# Check what format is actually in the database
print("\n" + "="*80)
print("ACTUAL PERIODE VALUES (sample):")
print("="*80)
samples = LW321.objects.values_list('periode', flat=True).distinct().order_by('-periode')[:20]
for s in samples:
    print(f"  '{s}'")

print("\n")
