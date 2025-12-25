from django.db.models import Sum, F, Case, When, Value, DecimalField, ExpressionWrapper, Count
from .utils import cast_to_decimal, safe_decimal_field

def annotate_metrics(queryset):
    """
    Annotates queryset with outstanding, SML, NPL, LR, LAR fields.
    - OS column from database (DecimalField)
    - Outstanding calculated, named 'outstanding' to avoid conflict
    - DPK/SML = SUM(OS) WHERE KOL_ADK = '2'
    - NPL = SUM(OS) WHERE KOL_ADK IN ('3', '4', '5')
    """
    qs = queryset.annotate(
        val_lancar=cast_to_decimal('kolektibilitas_lancar'),
        val_dpk=cast_to_decimal('kolektibilitas_dpk'),
        val_kl=cast_to_decimal('kolektibilitas_kurang_lancar'),
        val_d=cast_to_decimal('kolektibilitas_diragukan'),
        val_m=cast_to_decimal('kolektibilitas_macet'),
    )
    
    qs = qs.annotate(val_os=safe_decimal_field('os'))

    qs = qs.annotate(
        os_from_legacy=ExpressionWrapper(
            F('val_lancar') + F('val_dpk') + F('val_kl') + F('val_d') + F('val_m'),
            output_field=DecimalField(max_digits=20, decimal_places=2)
        )
    )
    
    qs = qs.annotate(
        outstanding=Case(
            When(val_os__gt=0, then=F('val_os')),
            default=F('os_from_legacy'),
            output_field=DecimalField(max_digits=20, decimal_places=2)
        )
    )

    qs = qs.annotate(
        npl=Case(
            When(kol_adk__in=['3', '4', '5'], val_os__gt=0, then=F('val_os')),
            When(kol_adk__in=['3', '4', '5'], val_os=0, then=F('val_kl') + F('val_d') + F('val_m')),
            default=Value(0),
            output_field=DecimalField(max_digits=20, decimal_places=2)
        )
    )

    qs = qs.annotate(
        sml=Case(
            When(kol_adk='2', val_os__gt=0, then=F('val_os')),
            When(kol_adk='2', val_os=0, then=F('val_dpk')),
            default=Value(0),
            output_field=DecimalField(max_digits=20, decimal_places=2)
        )
    )

    qs = qs.annotate(
        lr=Case(
            When(kol_adk='1', flag_restruk='Y', then=F('val_lancar')),
            default=Value(0),
            output_field=DecimalField(max_digits=20, decimal_places=2)
        )
    )

    qs = qs.annotate(
        lar=ExpressionWrapper(
            F('sml') + F('npl') + F('lr'),
            output_field=DecimalField(max_digits=20, decimal_places=2)
        )
    )

    return qs


def count_unique_customers(queryset, segment='SMALL'):
    """
    Counts total customers by summing NASABAH column for a given segment.
    This is used for NSB (Nasabah/Customer count) metric.
    
    FORMULA: SUM(NASABAH) WHERE segment=SMALL AND DUB_NASABAH='TRUE' (case-insensitive)
    
    Args:
        queryset: The base queryset to filter
        segment: The segment to filter by (default: 'SMALL')
    
    Returns:
        Sum of NASABAH field for unique customers (DUB_NASABAH='TRUE' or 'True')
    """
    from .segmentation import get_segment_annotation
    from django.db.models import Q
    
    # Annotate with segment
    qs = queryset.annotate(segment=get_segment_annotation())
    
    # Filter by segment and DUB_NASABAH = 'TRUE' (case-insensitive: 'TRUE', 'True', 'true')
    qs = qs.filter(
        segment=segment
    ).filter(
        Q(dub_nasabah__iexact='TRUE')  # Case-insensitive exact match
    )
    
    # Sum NASABAH column (handle NULL values)
    result = qs.aggregate(
        total_nasabah=Sum('nasabah')
    )
    
    # Return 0 if NULL
    return result['total_nasabah'] or 0
