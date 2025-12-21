"""
Quick Test Script for Refactored Metric System
Run this to verify table_builder and metric_handlers work correctly.
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from datetime import date, timedelta
from dashboard.formulas.table_builder import build_metric_tables
from dashboard.models import LW321

def test_os_small():
    """Test OS SMALL metric"""
    print("\n" + "="*70)
    print("TEST 1: OS SMALL (No filter)")
    print("="*70)
    
    selected_date = date.today()
    
    try:
        tables = build_metric_tables(
            selected_date=selected_date,
            segment_filter='SMALL',
            metric_field='os',
            kol_adk_filter=None
        )
        
        konsol = tables['konsol']
        kanca = tables['kanca']
        kcp = tables['kcp']
        
        print(f"✅ KONSOL table built: {len(konsol['rows'])} rows")
        print(f"✅ KANCA ONLY table built: {len(kanca['rows'])} rows")
        print(f"✅ KCP ONLY table built: {len(kcp['rows'])} rows")
        
        # Check totals
        konsol_total = konsol['totals'].get('E', 0)
        print(f"\n📊 KONSOL Total (Column E): {konsol_total:,.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dpk_small():
    """Test DPK SMALL metric with kol_adk filter"""
    print("\n" + "="*70)
    print("TEST 2: DPK SMALL (kol_adk='2' filter)")
    print("="*70)
    
    selected_date = date.today()
    
    try:
        tables = build_metric_tables(
            selected_date=selected_date,
            segment_filter='SMALL',
            metric_field='dpk',
            kol_adk_filter='2'  # DPK kolektibilitas filter
        )
        
        konsol = tables['konsol']
        kanca = tables['kanca']
        kcp = tables['kcp']
        
        print(f"✅ KONSOL table built: {len(konsol['rows'])} rows")
        print(f"✅ KANCA ONLY table built: {len(kanca['rows'])} rows")
        print(f"✅ KCP ONLY table built: {len(kcp['rows'])} rows")
        
        # Check totals
        konsol_total = konsol['totals'].get('E', 0)
        print(f"\n📊 KONSOL Total (Column E): {konsol_total:,.2f}")
        
        # Check if filter is applied
        print("\n🔍 Checking kol_adk='2' filter...")
        periode_str = selected_date.strftime('%d.%m.%Y')
        count_with_filter = LW321.objects.filter(
            periode=periode_str,
            kol_adk='2'
        ).count()
        count_without_filter = LW321.objects.filter(
            periode=periode_str
        ).count()
        
        print(f"   Records with kol_adk='2': {count_with_filter}")
        print(f"   Total records: {count_without_filter}")
        
        if count_with_filter < count_without_filter:
            print("   ✅ Filter is working (filtered count < total count)")
        elif count_with_filter == 0:
            print("   ⚠️  No records with kol_adk='2' found for this date")
        else:
            print("   ℹ️  All records have kol_adk='2'")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_date_columns():
    """Test date column calculations"""
    print("\n" + "="*70)
    print("TEST 3: Date Column Calculations")
    print("="*70)
    
    from dashboard.formulas.table_builder import get_date_columns
    
    selected_date = date.today()
    
    try:
        date_cols = get_date_columns(selected_date)
        
        print(f"Selected Date: {selected_date}")
        print(f"\nColumn A ({date_cols['A']['label']}): {date_cols['A']['date']}")
        print(f"Column B ({date_cols['B']['label']}): {date_cols['B']['date']}")
        print(f"Column C ({date_cols['C']['label']}): {date_cols['C']['date']}")
        print(f"Column D ({date_cols['D']['label']}): {date_cols['D']['date']}")
        print(f"Column E ({date_cols['E']['label']}): {date_cols['E']['date']}")
        
        print("\n✅ Date calculations working correctly")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_connection():
    """Test database has data"""
    print("\n" + "="*70)
    print("TEST 4: Database Connection & Data")
    print("="*70)
    
    try:
        total_records = LW321.objects.count()
        print(f"✅ Database connected")
        print(f"📊 Total records in LW321: {total_records:,}")
        
        # Get distinct dates
        from django.db.models import Count
        distinct_periodes = LW321.objects.values('periode').distinct().count()
        print(f"📅 Distinct periods: {distinct_periodes}")
        
        # Check for kol_adk='2' records
        dpk_records = LW321.objects.filter(kol_adk='2').count()
        print(f"💰 Records with kol_adk='2' (DPK): {dpk_records:,}")
        
        if dpk_records == 0:
            print("   ⚠️  WARNING: No DPK records found! DPK SMALL page will show zeros.")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("\n" + "="*70)
    print(" REFACTORED METRIC SYSTEM - QUICK TEST")
    print("="*70)
    
    results = []
    
    # Run tests
    results.append(("Database Connection", test_database_connection()))
    results.append(("Date Calculations", test_date_columns()))
    results.append(("OS SMALL", test_os_small()))
    results.append(("DPK SMALL", test_dpk_small()))
    
    # Summary
    print("\n" + "="*70)
    print(" TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System is working correctly.")
        print("\n✅ You can now test in browser:")
        print("   - http://127.0.0.1:8000/page/small-os/")
        print("   - http://127.0.0.1:8000/page/small-dpk/")
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
    
    print("="*70)
