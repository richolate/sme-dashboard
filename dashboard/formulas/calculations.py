from django.db.models import Sum, F, Case, When, Value, DecimalField, ExpressionWrapper, Count
from .utils import cast_to_decimal, safe_decimal_field

def annotate_metrics(queryset):
    """
    Annotates the queryset with outstanding, SML, NPL, LR, LAR fields.
    
    IMPORTANT: 
    - OS column already exists in database (from Excel file) as 'os' field (DecimalField)
    - Outstanding (calculated) will be named 'outstanding' to avoid conflict
    - DPK/SML = SUM(OS) WHERE KOL_ADK = '2'
    - NPL = SUM(OS) WHERE KOL_ADK IN ('3', '4', '5')
    """
    # First, ensure we have numeric values for the base fields
    # Keep legacy kolektibilitas fields for backward compatibility (these are CharFields)
    qs = queryset.annotate(
        val_lancar=cast_to_decimal('kolektibilitas_lancar'),
        val_dpk=cast_to_decimal('kolektibilitas_dpk'),
        val_kl=cast_to_decimal('kolektibilitas_kurang_lancar'),
        val_d=cast_to_decimal('kolektibilitas_diragukan'),
        val_m=cast_to_decimal('kolektibilitas_macet'),
    )
    
    # Safe access to OS field (already DecimalField in model, just handle NULL)
    qs = qs.annotate(
        val_os=safe_decimal_field('os')
    )

    # Calculate Outstanding from legacy fields (for fallback)
    qs = qs.annotate(
        os_from_legacy=ExpressionWrapper(
            F('val_lancar') + F('val_dpk') + F('val_kl') + F('val_d') + F('val_m'),
            output_field=DecimalField(max_digits=20, decimal_places=2)
        )
    )
    
    # Outstanding: Use OS from file (val_os) if not zero, otherwise use calculated from legacy
    # Rename to 'outstanding' to avoid conflict with model field 'os'
    qs = qs.annotate(
        outstanding=Case(
            When(val_os__gt=0, then=F('val_os')),
            default=F('os_from_legacy'),
            output_field=DecimalField(max_digits=20, decimal_places=2)
        )
    )

    # Calculate NPL (Non-Performing Loan)
    # NEW FORMULA: SUM(OS) WHERE KOL_ADK IN ('3', '4', '5')
    # Use val_os if > 0, otherwise use legacy calculation
    qs = qs.annotate(
        npl=Case(
            When(kol_adk__in=['3', '4', '5'], val_os__gt=0, then=F('val_os')),
            When(kol_adk__in=['3', '4', '5'], val_os=0, then=F('val_kl') + F('val_d') + F('val_m')),
            default=Value(0),
            output_field=DecimalField(max_digits=20, decimal_places=2)
        )
    )

    # Calculate SML (Special Mention Loan) / DPK
    # NEW FORMULA: SUM(OS) WHERE KOL_ADK = '2'
    # Use val_os if > 0, otherwise use legacy calculation
    qs = qs.annotate(
        sml=Case(
            When(kol_adk='2', val_os__gt=0, then=F('val_os')),
            When(kol_adk='2', val_os=0, then=F('val_dpk')),
            default=Value(0),
            output_field=DecimalField(max_digits=20, decimal_places=2)
        )
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
