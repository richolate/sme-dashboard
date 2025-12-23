from django.db.models import Sum, F, Case, When, Value, DecimalField, ExpressionWrapper, Count
from .utils import cast_to_decimal

def annotate_metrics(queryset):
    """
    Annotates the queryset with OS, SML, NPL, LR, LAR fields.
    """
    # First, ensure we have numeric values for the base fields
    qs = queryset.annotate(
        val_lancar=cast_to_decimal('kolektibilitas_lancar'),
        val_dpk=cast_to_decimal('kolektibilitas_dpk'),
        val_kl=cast_to_decimal('kolektibilitas_kurang_lancar'),
        val_d=cast_to_decimal('kolektibilitas_diragukan'),
        val_m=cast_to_decimal('kolektibilitas_macet'),
    )

    # Calculate OS (Outstanding)
    qs = qs.annotate(
        os=ExpressionWrapper(
            F('val_lancar') + F('val_dpk') + F('val_kl') + F('val_d') + F('val_m'),
            output_field=DecimalField(max_digits=20, decimal_places=2)
        )
    )

    # Calculate NPL (Non-Performing Loan)
    # NPL = KL + D + M
    qs = qs.annotate(
        npl=ExpressionWrapper(
            F('val_kl') + F('val_d') + F('val_m'),
            output_field=DecimalField(max_digits=20, decimal_places=2)
        )
    )

    # Calculate SML (Special Mention Loan)
    # SML = DPK only
    qs = qs.annotate(
        sml=F('val_dpk')
    )

    # Calculate LR (Loan Restructured - Current)
    # LR = Lancar if (kol_adk == '1' AND flag_restruk == 'Y')
    qs = qs.annotate(
        lr=Case(
            When(kol_adk='1', flag_restruk='Y', then=F('val_lancar')),
            default=Value(0),
            output_field=DecimalField(max_digits=20, decimal_places=2)
        )
    )

    # Calculate LAR (Loan at Risk)
    # LAR = SML + NPL + LR
    qs = qs.annotate(
        lar=ExpressionWrapper(
            F('sml') + F('npl') + F('lr'),
            output_field=DecimalField(max_digits=20, decimal_places=2)
        )
    )

    return qs


def count_unique_customers(queryset, segment='SMALL'):
    """
    Counts unique customers (distinct CIF_NO) for a given segment.
    This is used for NSB (Nasabah/Customer count) metric.
    
    Args:
        queryset: The base queryset to filter
        segment: The segment to filter by (default: 'SMALL')
    
    Returns:
        Count of distinct CIF_NO values
    """
    from .segmentation import get_segment_annotation
    
    # Annotate with segment
    qs = queryset.annotate(segment=get_segment_annotation())
    
    # Filter by segment
    qs = qs.filter(segment=segment)
    
    # Count distinct CIF_NO (field name is cif_no with underscore)
    return qs.values('cif_no').distinct().count()
