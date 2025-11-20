from django.db.models import Sum, F, Case, When, Value, DecimalField, ExpressionWrapper
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
    # SML = DPK + (Lancar if kol_adk == '2')
    # Assuming if kol_adk is 2, the Lancar portion is considered SML.
    qs = qs.annotate(
        sml=ExpressionWrapper(
            F('val_dpk') + Case(
                When(kol_adk='2', then=F('val_lancar')),
                default=Value(0),
                output_field=DecimalField(max_digits=20, decimal_places=2)
            ),
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
