import re
from datetime import datetime
from django.db.models import Case, When, Value, DecimalField, F, Func, CharField
from django.db.models.functions import Cast, Replace, Coalesce, NullIf

def cast_to_decimal(field_name):
    """
    Helper to cast a CharField to DecimalField safely.
    Handles empty strings, nulls, and whitespace by treating them as 0.
    
    NOTE: This function is for CharField fields only (kolektibilitas_*).
    For DecimalField (like 'os'), use Coalesce(F(field_name), Value(0)) directly.
    """
    # NullIf converts empty string to NULL, then Coalesce converts NULL to '0'
    # Replace handles comma decimals
    # This ensures we never try to cast an empty string to decimal
    return Cast(
        Coalesce(
            NullIf(
                Replace(F(field_name), Value(','), Value('.')),
                Value('')
            ),
            Value('0')
        ),
        output_field=DecimalField(max_digits=20, decimal_places=2)
    )

def safe_decimal_field(field_name):
    """
    Helper to safely use a DecimalField, converting NULL to 0.
    Use this for fields that are already DecimalField in model (like 'os').
    """
    return Coalesce(F(field_name), Value(0, output_field=DecimalField(max_digits=20, decimal_places=2)))

def extract_period_from_filename(filename):
    """
    Extracts date from filename in YYYY-MM-DD format.
    Returns the date string or None if not found.
    """
    match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if match:
        return match.group(1)
    return None
