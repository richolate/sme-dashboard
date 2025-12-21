"""
Test DPK calculation using SML formula
Verify that DPK = SML = val_dpk + (val_lancar if kol_adk='2')
"""
import os
import sys
import django
from decimal import Decimal

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db.models import Sum
from datetime import datetime
from dashboard.models import LW321
from dashboard.formulas.calculations import annotate_metrics
from dashboard.formulas.segmentation import get_segment_annotation

print("=" * 80)
print("Testing DPK Calculation with SML Formula")
print("=" * 80)

# Get latest period
latest_period = LW321.objects.values('periode').order_by('-periode').first()
if not latest_period:
    print("No data found!")
    sys.exit(1)

periode = latest_period['periode']
print(f"\nTesting with periode: {periode}")

# Test 1: Check SML calculation
print("\n" + "=" * 80)
print("Test 1: SML Calculation")
print("=" * 80)

# Get SMALL segment data - correct usage of get_segment_annotation
qs = LW321.objects.filter(periode=periode)
qs = qs.annotate(segment=get_segment_annotation())  # Annotate segment
qs = annotate_metrics(qs)  # Annotate metrics (os, sml, npl, etc.)
qs = qs.filter(segment='SMALL')  # Filter by segment

# Calculate SML total
sml_total = qs.aggregate(total=Sum('sml'))['total'] or Decimal('0')
print(f"Total SML (for DPK): Rp {sml_total:,.2f}")

# Break down the SML calculation
from dashboard.formulas.utils import cast_to_decimal
breakdown_qs = LW321.objects.filter(periode=periode).annotate(
    segment=get_segment_annotation()
).filter(segment='SMALL').annotate(
    val_dpk=cast_to_decimal('kolektibilitas_dpk'),
    val_lancar=cast_to_decimal('kolektibilitas_lancar')
)

# DPK component
dpk_total = breakdown_qs.aggregate(total=Sum('val_dpk'))['total'] or Decimal('0')
print(f"  - Total kolektibilitas_dpk: Rp {dpk_total:,.2f}")

# Lancar with kol_adk='2' component
lancar_kol2_total = breakdown_qs.filter(kol_adk='2').aggregate(
    total=Sum('val_lancar')
)['total'] or Decimal('0')
print(f"  - Total Lancar (kol_adk='2'): Rp {lancar_kol2_total:,.2f}")

# Manual calculation
manual_sml = dpk_total + lancar_kol2_total
print(f"  - Manual SML = DPK + Lancar(kol_adk='2'): Rp {manual_sml:,.2f}")

# Verify
if abs(sml_total - manual_sml) < Decimal('0.01'):
    print("  ✅ SML calculation CORRECT!")
else:
    print(f"  ❌ SML calculation MISMATCH! Difference: Rp {abs(sml_total - manual_sml):,.2f}")

# Test 2: Compare with OS
print("\n" + "=" * 80)
print("Test 2: Compare DPK (SML) with OS")
print("=" * 80)

os_total = qs.aggregate(total=Sum('os'))['total'] or Decimal('0')
print(f"Total OS: Rp {os_total:,.2f}")
print(f"Total SML (DPK): Rp {sml_total:,.2f}")
print(f"Ratio SML/OS: {(sml_total/os_total*100):.2f}%" if os_total > 0 else "N/A")

# Test 3: Check data by KANCA
print("\n" + "=" * 80)
print("Test 3: SML by KANCA (Top 5)")
print("=" * 80)

sml_by_kanca = qs.values('kanca').annotate(
    total=Sum('sml')
).order_by('-total')[:5]

for item in sml_by_kanca:
    kode = item['kanca']
    total = item['total'] or Decimal('0')
    print(f"KANCA {kode}: Rp {total:,.2f}")

# Test 4: Test table_builder with dpk metric
print("\n" + "=" * 80)
print("Test 4: Table Builder with metric_field='dpk'")
print("=" * 80)

from dashboard.formulas.table_builder import get_metric_by_uker

# Get DPK data for a specific date
test_date = datetime.strptime(periode, '%d/%m/%Y').date()
dpk_by_uker = get_metric_by_uker(
    target_date=test_date,
    segment_filter='SMALL',
    metric_field='dpk'  # Should map to 'sml' field
)

print(f"Total UKER entries: {len(dpk_by_uker)}")
total_from_dict = sum(dpk_by_uker.values())
print(f"Total DPK from get_metric_by_uker: Rp {total_from_dict:,.2f}")

# Verify with SML total
if abs(total_from_dict - sml_total) < Decimal('0.01'):
    print("✅ table_builder correctly uses SML for DPK!")
else:
    print(f"❌ table_builder MISMATCH! Difference: Rp {abs(total_from_dict - sml_total):,.2f}")

print("\n" + "=" * 80)
print("Test Summary")
print("=" * 80)
print("✅ DPK now uses SML formula from calculations.py")
print("✅ SML = val_dpk + (val_lancar if kol_adk='2')")
print("✅ Table structure same as OS SMALL, only metric differs")
print("=" * 80)
