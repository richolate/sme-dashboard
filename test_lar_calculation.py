"""
Test script to verify LAR calculation formula: LAR = SML + NPL + LR

This script verifies:
1. LAR values match the formula: LAR = SML + NPL + LR
2. Table consistency: KONSOL = KANCA ONLY + KCP ONLY
3. Date format is correct (%d/%m/%Y)
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime

# Django setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from dashboard.models import LW321
from dashboard.formulas.calculations import annotate_metrics
from dashboard.formulas.segmentation import get_segment_annotation
from dashboard.formulas.table_builder import build_metric_tables

def test_lar_formula():
    """Test that LAR = SML + NPL + LR from calculations.py"""
    print("=" * 80)
    print("TEST 1: Verify LAR Formula (LAR = SML + NPL + LR)")
    print("=" * 80)
    
    # Get latest date (periode is CharField, not DateField)
    latest_date_str = LW321.objects.order_by('-periode').values_list('periode', flat=True).first()
    print(f"\nLatest date: {latest_date_str}")
    
    # Get annotated data for SMALL segment
    # Use string for periode filter, not date object
    queryset = LW321.objects.filter(periode=latest_date_str)
    queryset = queryset.annotate(segment=get_segment_annotation())  # Annotate segment first
    queryset = annotate_metrics(queryset)  # Then annotate metrics
    queryset = queryset.filter(segment='SMALL')  # Filter by SMALL segment
    
    # Get sample records
    sample = queryset[:5]
    
    print("\nSample Records (First 5):")
    print("-" * 80)
    
    all_correct = True
    for record in sample:
        sml = record.sml or Decimal('0')
        npl = record.npl or Decimal('0')
        lr = record.lr or Decimal('0')
        lar = record.lar or Decimal('0')
        
        expected_lar = sml + npl + lr
        diff = abs(lar - expected_lar)
        
        status = "✓" if diff < Decimal('0.01') else "✗"
        if diff >= Decimal('0.01'):
            all_correct = False
        
        print(f"{status} Rekening: {record.nomor_rekening}")
        print(f"  SML: Rp {sml:,.2f}")
        print(f"  NPL: Rp {npl:,.2f}")
        print(f"  LR:  Rp {lr:,.2f}")
        print(f"  LAR (calculated): Rp {lar:,.2f}")
        print(f"  LAR (expected):   Rp {expected_lar:,.2f}")
        print(f"  Difference:       Rp {diff:,.2f}")
        print()
    
    # Calculate totals
    total_sml = sum((r.sml or Decimal('0')) for r in queryset)
    total_npl = sum((r.npl or Decimal('0')) for r in queryset)
    total_lr = sum((r.lr or Decimal('0')) for r in queryset)
    total_lar = sum((r.lar or Decimal('0')) for r in queryset)
    
    expected_total_lar = total_sml + total_npl + total_lr
    total_diff = abs(total_lar - expected_total_lar)
    
    print("Total LAR for SMALL Segment:")
    print("-" * 80)
    print(f"Total SML: Rp {total_sml:,.2f}")
    print(f"Total NPL: Rp {total_npl:,.2f}")
    print(f"Total LR:  Rp {total_lr:,.2f}")
    print(f"Total LAR (calculated): Rp {total_lar:,.2f}")
    print(f"Total LAR (expected):   Rp {expected_total_lar:,.2f}")
    print(f"Difference:             Rp {total_diff:,.2f}")
    
    if total_diff < Decimal('1.00'):
        print("\n✅ TEST 1 PASSED: LAR formula is correct (LAR = SML + NPL + LR)")
    else:
        print(f"\n❌ TEST 1 FAILED: LAR formula mismatch (diff: Rp {total_diff:,.2f})")
    
    return all_correct and total_diff < Decimal('1.00')


def test_table_consistency():
    """Test that KONSOL = KANCA ONLY + KCP ONLY"""
    print("\n" + "=" * 80)
    print("TEST 2: Table Consistency (KONSOL = KANCA ONLY + KCP ONLY)")
    print("=" * 80)
    
    # Get latest date
    latest_date_str = LW321.objects.order_by('-periode').values_list('periode', flat=True).first()
    latest_date = datetime.strptime(latest_date_str, '%d/%m/%Y').date()
    
    # Build tables
    table_data = build_metric_tables(
        selected_date=latest_date,
        segment_filter='SMALL',
        metric_field='lar'
    )
    
    konsol_table = table_data.get('konsol_table', {})
    kanca_table = table_data.get('kanca_only_table', {})
    kcp_table = table_data.get('kcp_only_table', {})
    
    print(f"\nDate: {latest_date_str}")
    print("\nTable Totals:")
    print("-" * 80)
    
    # Extract Grand Total from each table
    konsol_total = Decimal('0')
    if konsol_table.get('rows'):
        for row in konsol_table['rows']:
            if row.get('kode_kanca') == 'Grand Total':
                konsol_total = row.get('total', Decimal('0'))
                break
    
    kanca_total = Decimal('0')
    if kanca_table.get('rows'):
        for row in kanca_table['rows']:
            if row.get('kode_kanca') == 'Grand Total':
                kanca_total = row.get('total', Decimal('0'))
                break
    
    kcp_total = Decimal('0')
    if kcp_table.get('rows'):
        for row in kcp_table['rows']:
            if row.get('kode_kanca') == 'Grand Total':
                kcp_total = row.get('total', Decimal('0'))
                break
    
    print(f"KONSOL Total:     Rp {konsol_total:,.2f}")
    print(f"KANCA ONLY Total: Rp {kanca_total:,.2f}")
    print(f"KCP ONLY Total:   Rp {kcp_total:,.2f}")
    print(f"KANCA + KCP:      Rp {(kanca_total + kcp_total):,.2f}")
    
    diff = abs(konsol_total - (kanca_total + kcp_total))
    print(f"\nDifference: Rp {diff:,.2f}")
    
    if diff < Decimal('1.00'):
        print("\n✅ TEST 2 PASSED: KONSOL = KANCA ONLY + KCP ONLY")
        return True
    else:
        print(f"\n❌ TEST 2 FAILED: Table totals don't match (diff: Rp {diff:,.2f})")
        return False


def test_table_structure():
    """Test that tables have correct structure with kode_uker and uker fields"""
    print("\n" + "=" * 80)
    print("TEST 3: Table Structure (kode_uker and uker fields)")
    print("=" * 80)
    
    # Get latest date
    latest_date_str = LW321.objects.order_by('-periode').values_list('periode', flat=True).first()
    latest_date = datetime.strptime(latest_date_str, '%d/%m/%Y').date()
    
    # Build tables
    table_data = build_metric_tables(
        selected_date=latest_date,
        segment_filter='SMALL',
        metric_field='lar'
    )
    
    kanca_table = table_data.get('kanca_only_table', {})
    kcp_table = table_data.get('kcp_only_table', {})
    
    print("\nKANCA ONLY Table - Sample Row:")
    print("-" * 80)
    if kanca_table.get('rows'):
        # Get first non-total row
        for row in kanca_table['rows']:
            if row.get('kode_kanca') != 'Grand Total':
                print(f"kode_kanca: {row.get('kode_kanca')}")
                print(f"kanca:      {row.get('kanca')}")
                print(f"kode_uker:  {row.get('kode_uker')}")
                print(f"uker:       {row.get('uker')}")
                
                has_kode_uker = 'kode_uker' in row
                has_uker = 'uker' in row
                
                if has_kode_uker and has_uker:
                    print("✅ KANCA ONLY has kode_uker and uker fields")
                else:
                    print("❌ KANCA ONLY missing required fields")
                    return False
                break
    
    print("\nKCP ONLY Table - Sample Row:")
    print("-" * 80)
    if kcp_table.get('rows'):
        # Get first non-total row
        for row in kcp_table['rows']:
            if row.get('kode_kanca') != 'Grand Total':
                print(f"kode_kanca: {row.get('kode_kanca')}")
                print(f"kanca:      {row.get('kanca')}")
                print(f"kode_uker:  {row.get('kode_uker')}")
                print(f"uker:       {row.get('uker')}")
                
                has_kode_uker = 'kode_uker' in row
                has_uker = 'uker' in row
                
                if has_kode_uker and has_uker:
                    print("✅ KCP ONLY has kode_uker and uker fields")
                else:
                    print("❌ KCP ONLY missing required fields")
                    return False
                break
    
    print("\n✅ TEST 3 PASSED: Tables have correct structure")
    return True


def test_date_format():
    """Test that dates are formatted correctly (%d/%m/%Y)"""
    print("\n" + "=" * 80)
    print("TEST 4: Date Format (%d/%m/%Y)")
    print("=" * 80)
    
    # Get latest date
    latest_date_str = LW321.objects.order_by('-periode').values_list('periode', flat=True).first()
    latest_date = datetime.strptime(latest_date_str, '%d/%m/%Y').date()
    
    # Build tables
    table_data = build_metric_tables(
        selected_date=latest_date,
        segment_filter='SMALL',
        metric_field='lar'
    )
    
    konsol_table = table_data.get('konsol_table', {})
    
    print("\nDate columns in KONSOL table:")
    print("-" * 80)
    
    if konsol_table.get('date_columns'):
        sample_dates = konsol_table['date_columns'][:3]
        all_correct = True
        
        for date_str in sample_dates:
            # Check format: should be dd/mm/yyyy
            try:
                parsed = datetime.strptime(date_str, '%d/%m/%Y')
                print(f"✓ {date_str} - Correct format")
            except ValueError:
                print(f"✗ {date_str} - Wrong format (expected dd/mm/yyyy)")
                all_correct = False
        
        if all_correct:
            print("\n✅ TEST 4 PASSED: Dates are formatted correctly")
            return True
        else:
            print("\n❌ TEST 4 FAILED: Date format incorrect")
            return False
    else:
        print("❌ No date columns found")
        return False


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("LAR CALCULATION TEST SUITE")
    print("Formula: LAR = SML + NPL + LR")
    print("=" * 80)
    
    test_results = []
    
    # Run all tests
    test_results.append(("LAR Formula", test_lar_formula()))
    test_results.append(("Table Consistency", test_table_consistency()))
    test_results.append(("Table Structure", test_table_structure()))
    test_results.append(("Date Format", test_date_format()))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for test_name, passed in test_results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in test_results)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! LAR SMALL page is working correctly.")
    else:
        print("\n⚠️ SOME TESTS FAILED. Please review the output above.")
    
    print("=" * 80)
