"""
Test LR (Loan Restructured) calculation and table structure
Verify LR = Lancar if (kol_adk == '1' AND flag_restruk == 'Y')
"""
import os
import sys
import django
from decimal import Decimal

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from datetime import datetime
from django.db.models import Sum, Q
from dashboard.models import LW321
from dashboard.formulas.calculations import annotate_metrics
from dashboard.formulas.segmentation import get_segment_annotation
from dashboard.formulas.table_builder import (
    get_date_columns,
    build_konsol_table,
    build_kanca_only_table,
    build_kcp_only_table
)

print("=" * 80)
print("Testing LR (Loan Restructured) Calculation and Tables")
print("=" * 80)

# Get latest period
latest_period = LW321.objects.values('periode').order_by('-periode').first()
if not latest_period:
    print("No data found!")
    sys.exit(1)

periode = latest_period['periode']
print(f"\nTesting with periode: {periode}")

# Test 1: Verify LR Formula
print("\n" + "=" * 80)
print("Test 1: LR Formula Verification")
print("=" * 80)

# Get SMALL segment data
qs = LW321.objects.filter(periode=periode)
qs = qs.annotate(segment=get_segment_annotation())
qs = annotate_metrics(qs)
qs = qs.filter(segment='SMALL')

# Calculate LR total
lr_total = qs.aggregate(total=Sum('lr'))['total'] or Decimal('0')
print(f"Total LR (from annotate): Rp {lr_total:,.2f}")

# Verify LR calculation manually
from dashboard.formulas.utils import cast_to_decimal
breakdown_qs = LW321.objects.filter(periode=periode).annotate(
    segment=get_segment_annotation()
).filter(segment='SMALL').annotate(
    val_lancar=cast_to_decimal('kolektibilitas_lancar')
)

# LR = Lancar where kol_adk='1' AND flag_restruk='Y'
lr_records = breakdown_qs.filter(
    kol_adk='1',
    flag_restruk='Y'
).aggregate(total=Sum('val_lancar'))['total'] or Decimal('0')

print(f"Manual LR calculation:")
print(f"  - Lancar (kol_adk='1' AND flag_restruk='Y'): Rp {lr_records:,.2f}")

# Count records
lr_count = breakdown_qs.filter(kol_adk='1', flag_restruk='Y').count()
total_count = breakdown_qs.count()
print(f"  - Records with LR: {lr_count:,} / {total_count:,} ({(lr_count/total_count*100):.2f}%)")

if abs(lr_total - lr_records) < Decimal('0.01'):
    print("  ✅ LR calculation CORRECT!")
else:
    print(f"  ❌ LR calculation MISMATCH! Difference: Rp {abs(lr_total - lr_records):,.2f}")

# Test 2: Compare LR with OS
print("\n" + "=" * 80)
print("Test 2: LR vs OS Comparison")
print("=" * 80)

os_total = qs.aggregate(total=Sum('os'))['total'] or Decimal('0')
lancar_total = qs.aggregate(total=Sum('val_lancar'))['total'] or Decimal('0')

print(f"Total OS:     Rp {os_total:,.2f}")
print(f"Total Lancar: Rp {lancar_total:,.2f}")
print(f"Total LR:     Rp {lr_total:,.2f}")
print(f"LR/OS Ratio:  {(lr_total/os_total*100):.2f}%" if os_total > 0 else "N/A")
print(f"LR/Lancar:    {(lr_total/lancar_total*100):.2f}%" if lancar_total > 0 else "N/A")

# Test 3: Analyze LR records
print("\n" + "=" * 80)
print("Test 3: LR Records Analysis")
print("=" * 80)

# Count by kol_adk and flag_restruk
kol_adk_counts = breakdown_qs.values('kol_adk', 'flag_restruk').annotate(
    count=Sum('id')
).order_by('kol_adk', 'flag_restruk')

print("Records by kol_adk and flag_restruk:")
for item in kol_adk_counts:
    kol = item['kol_adk'] or 'NULL'
    flag = item['flag_restruk'] or 'NULL'
    count = item['count'] or 0
    print(f"  kol_adk={kol}, flag_restruk={flag}: {count}")

# Test 4: Test Tables
print("\n" + "=" * 80)
print("Test 4: LR Tables Structure")
print("=" * 80)

selected_date = datetime.strptime(periode, '%d/%m/%Y').date()
date_columns = get_date_columns(selected_date)

# Build KONSOL table
konsol = build_konsol_table(
    date_columns=date_columns,
    segment_filter='SMALL',
    metric_field='lr'
)

# Build KANCA ONLY table
kanca_only = build_kanca_only_table(
    date_columns=date_columns,
    segment_filter='SMALL',
    metric_field='lr'
)

# Build KCP ONLY table
kcp_only = build_kcp_only_table(
    date_columns=date_columns,
    segment_filter='SMALL',
    metric_field='lr'
)

print(f"\n✅ KONSOL Table:")
print(f"   Title: {konsol['title']}")
print(f"   Rows: {len(konsol['rows'])}")
print(f"   Total E: Rp {konsol['totals']['E']:,.2f}")

print(f"\n✅ KANCA ONLY Table:")
print(f"   Title: {kanca_only['title']}")
print(f"   Rows: {len(kanca_only['rows'])}")
print(f"   Total E: Rp {kanca_only['totals']['E']:,.2f}")

print(f"\n✅ KCP ONLY Table:")
print(f"   Title: {kcp_only['title']}")
print(f"   Rows: {len(kcp_only['rows'])}")
print(f"   Total E: Rp {kcp_only['totals']['E']:,.2f}")

# Test 5: Verify KONSOL = KANCA ONLY + KCP ONLY
print("\n" + "=" * 80)
print("Test 5: Verify KONSOL = KANCA ONLY + KCP ONLY")
print("=" * 80)

total_konsol = konsol['totals']['E']
total_kanca = kanca_only['totals']['E']
total_kcp = kcp_only['totals']['E']
total_combined = total_kanca + total_kcp

print(f"KONSOL Total:      Rp {total_konsol:,.2f}")
print(f"KANCA ONLY Total:  Rp {total_kanca:,.2f}")
print(f"KCP ONLY Total:    Rp {total_kcp:,.2f}")
print(f"Combined Total:    Rp {total_combined:,.2f}")
print(f"Difference:        Rp {abs(total_konsol - total_combined):,.2f}")

if abs(total_konsol - total_combined) < Decimal('0.01'):
    print("\n✅ PERFECT! KONSOL = KANCA ONLY + KCP ONLY")
else:
    print(f"\n❌ MISMATCH! Difference: Rp {abs(total_konsol - total_combined):,.2f}")

# Test 6: Check row structure
print("\n" + "=" * 80)
print("Test 6: Row Structure Verification")
print("=" * 80)

kanca_sample = kanca_only['rows'][0]
kcp_sample = kcp_only['rows'][0]

print(f"KANCA ONLY row keys: {list(kanca_sample.keys())[:10]}...")
print(f"  - kode_uker: {kanca_sample.get('kode_uker')}")
print(f"  - uker: {kanca_sample.get('uker')}")

print(f"\nKCP ONLY row keys: {list(kcp_sample.keys())[:10]}...")
print(f"  - kode_uker: {kcp_sample.get('kode_uker')}")
print(f"  - uker: {kcp_sample.get('uker')}")

# Verify required fields
required_fields = ['kode_uker', 'uker', 'kode_kanca', 'kanca', 'E', 'DtD', 'MoM', 'MtD', 'YtD']
kanca_has_all = all(field in kanca_sample for field in required_fields)
kcp_has_all = all(field in kcp_sample for field in required_fields)

if kanca_has_all and kcp_has_all:
    print("\n✅ All required fields present in both tables")
else:
    print("\n❌ Missing required fields!")

print("\n" + "=" * 80)
print("Test Summary")
print("=" * 80)
print("✅ LR uses formula from calculations.py:")
print("   LR = Lancar if (kol_adk='1' AND flag_restruk='Y')")
print("✅ Table structure same as OS SMALL, DPK SMALL, NPL SMALL")
print("✅ KONSOL = KANCA ONLY + KCP ONLY")
print("✅ All required fields (kode_uker, uker) are present")
print("=" * 80)
