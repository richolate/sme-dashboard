"""
Debug script to check KC Bandung Dewi Sartika calculation
KC Dewi Sartika is code 286, under KANCA 181 (Bandung)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from dashboard.models import LW321
from dashboard.formulas.calculations import annotate_metrics
from dashboard.formulas.segmentation import get_segment_annotation
from dashboard.formulas.table_builder import get_metric_by_uker, get_metric_by_kanca
from datetime import datetime, date
from decimal import Decimal

# Test date (from user's page: 2025-11-30)
test_date = date(2025, 11, 30)
KC_DEWI_SARTIKA = '286'
KANCA_BANDUNG = 181

print(f"Testing for date: {test_date}")
print(f"KC Bandung Dewi Sartika: {KC_DEWI_SARTIKA}")
print(f"Parent KANCA: {KANCA_BANDUNG}")
print("=" * 80)

# Method 1: Direct query with annotations
print("\n=== METHOD 1: Direct Query ===")
test_date_str = test_date.strftime('%d/%m/%Y')
qs = LW321.objects.filter(periode=test_date_str, kode_uker=KC_DEWI_SARTIKA)
qs = qs.annotate(segment=get_segment_annotation())
qs = annotate_metrics(qs)

# Filter for SMALL segment
records = qs.filter(segment='SMALL')
print(f"Total records (SMALL): {records.count()}")

# Group by kol_adk
print("\nBreakdown by kol_adk:")
for kol_adk in ['1', '2', '3', '4', '5']:
    kol_records = records.filter(kol_adk=kol_adk)
    total_sml = sum(r.sml or Decimal('0') for r in kol_records)
    total_os = sum(r.os or Decimal('0') for r in kol_records)
    count = kol_records.count()
    
    print(f"  kol_adk='{kol_adk}': {count} records, SML={total_sml:,.0f}, OS={total_os:,.0f}")

# Total DPK and OS
total_dpk_annotated = sum(r.sml or Decimal('0') for r in records)
total_os = sum(r.os or Decimal('0') for r in records)

print(f"\nDPK (from SML annotation): {total_dpk_annotated:,.0f}")
print(f"OS (all kol_adk): {total_os:,.0f}")

if total_os > 0:
    pct1 = (total_dpk_annotated / total_os) * 100
    print(f"%DPK (Method 1): {pct1:.2f}%")

# Method 2: Using get_metric_by_uker (like dashboard does)
print("\n=== METHOD 2: get_metric_by_uker ===")
dpk_by_uker = get_metric_by_uker(test_date, 'SMALL', 'sml', kol_adk_filter='2')
os_by_uker = get_metric_by_uker(test_date, 'SMALL', 'os', kol_adk_filter=None)

dpk_286 = dpk_by_uker.get(KC_DEWI_SARTIKA, Decimal('0'))
os_286 = os_by_uker.get(KC_DEWI_SARTIKA, Decimal('0'))

print(f"DPK for {KC_DEWI_SARTIKA}: {dpk_286:,.0f}")
print(f"OS for {KC_DEWI_SARTIKA}: {os_286:,.0f}")

if os_286 > 0:
    pct2 = (dpk_286 / os_286) * 100
    print(f"%DPK (Method 2): {pct2:.2f}%")

# Method 3: Using dpk_pct metric (like the page does)
print("\n=== METHOD 3: dpk_pct metric (dashboard method) ===")
dpk_pct_by_uker = get_metric_by_uker(test_date, 'SMALL', 'dpk_pct', kol_adk_filter=None)
dpk_pct_286 = dpk_pct_by_uker.get(KC_DEWI_SARTIKA, Decimal('0'))

print(f"%DPK for {KC_DEWI_SARTIKA} (direct): {dpk_pct_286:.2f}%")

print(f"\n{'='*80}")
print("ANALYSIS:")
print(f"  DPK (database): {total_dpk_annotated:,.0f}")
print(f"  DPK (in thousands): {total_dpk_annotated/1000:,.0f}")
print(f"  DPK (user says): 15,823")
print()
print(f"  OS (database, all kol_adk): {total_os:,.0f}")
print(f"  OS (in thousands): {total_os/1000:,.0f}")
print(f"  OS (user says): 270,775")
print()
print(f"  OS (database, kol_adk='2' only): {total_dpk_annotated:,.0f}")  
print(f"  OS kol_adk='2' (in thousands): {total_dpk_annotated/1000:,.0f}")
print()
print(f"  User calculation: 15,823 / 270,775 × 100 = 5.84%")
print(f"  Dashboard (all kol_adk): {total_dpk_annotated/1000:,.0f} / {total_os/1000:,.0f} × 100 = {pct1:.2f}%")
print(f"  If OS=kol_adk='2': {total_dpk_annotated/1000:,.0f} / {total_dpk_annotated/1000:,.0f} × 100 = 100.00%")
print()
print("CONCLUSION:")
print(f"  User expects OS to be {270775000 - total_os/1000:,.0f} thousand MORE than database")
print(f"  This is roughly {((270775000 - total_os/1000) / (total_os/1000)) * 100:.2f}% difference")
print()
print("  Possible reasons:")
print("  1. User looking at different date")
print("  2. User looking at different UKER (not just KC 286)")
print("  3. User looking at KANCA level (181 Bandung), not KCP level (286 Dewi Sartika)")

print(f"\n{'='*80}")
print("Let's check KANCA 181 (Bandung) instead of KC 286 (Dewi Sartika)...")

# Check KANCA 181
from dashboard.formulas.table_builder import get_metric_by_kanca
kanca_dpk = get_metric_by_kanca(test_date, 'SMALL', 'sml', '2')
kanca_os = get_metric_by_kanca(test_date, 'SMALL', 'os', None)

dpk_181 = kanca_dpk.get(181, Decimal('0'))
os_181 = kanca_os.get(181, Decimal('0'))

print(f"\nKANCA 181 (Bandung):")
print(f"  DPK: {dpk_181:,.0f} = {dpk_181/1000:,.0f} thousand")
print(f"  OS: {os_181:,.0f} = {os_181/1000:,.0f} thousand")
if os_181 > 0:
    pct_181 = (dpk_181 / os_181) * 100
    print(f"  %DPK: {pct_181:.2f}%")

print(f"\n{'='*80}")
print("EXPECTED from user:")
print("  DPK = 15,823")
print("  OS = 270,775")
print("  %DPK = 5.84%")
print("\nDashboard shows: 5.91%")

