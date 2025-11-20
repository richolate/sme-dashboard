import os
import sys
import django
from pathlib import Path

# Setup Django environment
# Get the project root directory (3 levels up from this file: dashboard/formulas/test_formula.py)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Now we can import Django models
from dashboard.models import LW321
from dashboard.formulas import annotate_metrics, get_segment_annotation, filter_by_uker

def run_test():
    print("Starting test...")
    
    # 1. Start with base queryset
    qs = LW321.objects.all()
    
    count = qs.count()
    print(f"Total records found: {count}")

    if count == 0:
        print("No data found in LW321 table.")
        return

    # 2. Apply Segmentation
    qs = qs.annotate(segment=get_segment_annotation())

    # 3. Calculate Metrics (OS, NPL, LAR, etc.)
    qs = annotate_metrics(qs)

    # 4. Filter (optional) - Commented out to see all data first
    # qs = filter_by_uker(qs, "KC Bandung Kopo")

    # Now you can use the calculated fields
    print("\nTop 5 Records:")
    print(f"{'Account':<20} | {'Segment':<10} | {'OS':<20} | {'NPL':<20} | {'LAR':<20}")
    print("-" * 100)
    
    for item in qs[:5]:
        # Handle None values for printing
        os_val = item.os if item.os is not None else 0
        npl_val = item.npl if item.npl is not None else 0
        lar_val = item.lar if item.lar is not None else 0
        
        print(f"{item.nomor_rekening:<20} | {item.segment:<10} | {os_val:,.2f} | {npl_val:,.2f} | {lar_val:,.2f}")

if __name__ == "__main__":
    run_test()