from datetime import datetime
from django.db.models import Q

def filter_by_period(queryset, period_str):
    """
    Filters the queryset by period.
    period_str should be in 'YYYY-MM-DD' format.
    """
    return queryset.filter(periode=period_str)

def filter_by_uker(queryset, uker_query):
    """
    Filters by KANCA, KODE_UKER, or UKER.
    """
    return queryset.filter(
        Q(kanca__icontains=uker_query) |
        Q(kode_uker__icontains=uker_query) |
        Q(uker__icontains=uker_query)
    )
