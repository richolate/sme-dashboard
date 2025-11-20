import re
from datetime import datetime
from django.db.models import Case, When, Value, DecimalField, F, Func
from django.db.models.functions import Cast, Replace

def cast_to_decimal(field_name):
    """
    Helper to cast a CharField to DecimalField.
    Handles empty strings and nulls by treating them as 0.
    """
    return Case(
        When(**{f"{field_name}__isnull": True}, then=Value(0)),
        When(**{f"{field_name}__exact": ''}, then=Value(0)),
        default=Cast(
            Replace(F(field_name), Value(','), Value('.')), # Handle potential comma decimals
            output_field=DecimalField(max_digits=20, decimal_places=2)
        ),
        output_field=DecimalField(max_digits=20, decimal_places=2)
    )

def extract_period_from_filename(filename):
    """
    Extracts date from filename in YYYY-MM-DD format.
    Returns the date string or None if not found.
    """
    match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if match:
        return match.group(1)
    return None
