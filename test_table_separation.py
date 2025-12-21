"""
Test KANCA ONLY and KCP ONLY tables
Verify that totals from KANCA ONLY + KCP ONLY = KONSOL
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
from dashboard.formulas.table_builder import (
    get_date_columns,
    build_konsol_table,
    build_kanca_only_table,
    build_kcp_only_table
)

print("=" * 80)
print("Testing KANCA ONLY and KCP ONLY Tables for DPK")
print("=" * 80)

# Get date columns for testing
selected_date = datetime(2025, 12, 31).date()
date_columns = get_date_columns(selected_date)

print(f"\nTesting with date: {selected_date}")
print(f"Date E (selected): {date_columns['E']['date']}")

# Test 1: Build KONSOL table
print("\n" + "=" * 80)
print("Test 1: KONSOL Table (KANCA + KCP)")
print("=" * 80)

konsol = build_konsol_table(
    date_columns=date_columns,
    segment_filter='SMALL',
    metric_field='dpk'
)

print(f"Title: {konsol['title']}")
print(f"Total rows: {len(konsol['rows'])}")
print(f"Total E (Konsol): Rp {konsol['totals']['E']:,.2f}")

# Show top 5 KANCA
print(f"\nTop 5 KANCA by E value:")
sorted_rows = sorted(konsol['rows'], key=lambda x: x['E'], reverse=True)[:5]
for row in sorted_rows:
    print(f"  {row['kanca']}: Rp {row['E']:,.2f}")

# Test 2: Build KANCA ONLY table
print("\n" + "=" * 80)
print("Test 2: KANCA ONLY Table (KANCA without KCP)")
print("=" * 80)

kanca_only = build_kanca_only_table(
    date_columns=date_columns,
    segment_filter='SMALL',
    metric_field='dpk'
)

print(f"Title: {kanca_only['title']}")
print(f"Total rows: {len(kanca_only['rows'])}")
print(f"Total E (KANCA ONLY): Rp {kanca_only['totals']['E']:,.2f}")

# Show top 5 KANCA ONLY
print(f"\nTop 5 KANCA ONLY by E value:")
sorted_kanca = sorted(kanca_only['rows'], key=lambda x: x['E'], reverse=True)[:5]
for row in sorted_kanca:
    print(f"  {row['kanca']}: Rp {row['E']:,.2f}")

# Test 3: Build KCP ONLY table
print("\n" + "=" * 80)
print("Test 3: KCP ONLY Table")
print("=" * 80)

kcp_only = build_kcp_only_table(
    date_columns=date_columns,
    segment_filter='SMALL',
    metric_field='dpk'
)

print(f"Title: {kcp_only['title']}")
print(f"Total rows: {len(kcp_only['rows'])}")
print(f"Total E (KCP ONLY): Rp {kcp_only['totals']['E']:,.2f}")

# Show top 5 KCP
print(f"\nTop 5 KCP by E value:")
sorted_kcp = sorted(kcp_only['rows'], key=lambda x: x['E'], reverse=True)[:5]
for row in sorted_kcp:
    print(f"  {row['kanca']}: Rp {row['E']:,.2f}")

# Test 4: Verify KONSOL = KANCA ONLY + KCP ONLY
print("\n" + "=" * 80)
print("Test 4: Verify KONSOL = KANCA ONLY + KCP ONLY")
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

# Test 5: Check if all tables have data
print("\n" + "=" * 80)
print("Test 5: Data Presence Check")
print("=" * 80)

checks = [
    ("KONSOL has data", konsol['totals']['E'] > 0),
    ("KANCA ONLY has data", kanca_only['totals']['E'] > 0),
    ("KCP ONLY has data", kcp_only['totals']['E'] > 0),
    ("KONSOL has rows", len(konsol['rows']) > 0),
    ("KANCA ONLY has rows", len(kanca_only['rows']) > 0),
    ("KCP ONLY has rows", len(kcp_only['rows']) > 0),
]

all_pass = True
for check_name, result in checks:
    status = "✅" if result else "❌"
    print(f"{status} {check_name}")
    if not result:
        all_pass = False

print("\n" + "=" * 80)
if all_pass:
    print("🎉 ALL TESTS PASSED!")
    print("✅ KANCA ONLY and KCP ONLY tables now have data")
    print("✅ KONSOL = KANCA ONLY + KCP ONLY")
else:
    print("⚠️ SOME TESTS FAILED")
print("=" * 80)
