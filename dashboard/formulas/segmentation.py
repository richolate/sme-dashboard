from django.db.models import Case, When, Value, CharField

SEGMENT_MAPPING = {
    "CC": [
        "RITKOM - CASHCOL RITEL (> Rp 1 M S/D Rp 25 M)",
        "RITKOM - CASHCOL MENENGAH (> Rp 25 M S/D Rp 200 M)",
        "RITKOM - CASHCOL KECIL (S/D Rp 1 M)",
    ],
    "SMALL": [
        "06. RITKOM -> Rp 1 M S/D Rp 2 M",
        "07. RITKOM -> Rp 2 M S/D Rp 3 M",
        "08. RITKOM -> Rp 3 M S/D Rp 4 M",
        "09. RITKOM -> Rp 4 M S/D Rp 5 M",
        "(PRT) 01. RITKOM -> Rp 1 M S/D Rp 2 M",
        "(PRT) 02. RITKOM -> Rp 2 M S/D Rp 3 M",
        "(PRT) 03. RITKOM -> Rp 3 M S/D Rp 4 M",
        "(PRT) 04. RITKOM -> Rp 4 M S/D Rp 5 M",
        "KREDIT PANGAN",
        "01. KECIL - S/D Rp 50 JUTA",
        "02. KECIL - > Rp.50 JUTA S/D Rp 100 JUTA",
        "03. KECIL - > Rp 100 JUTA S/D Rp 350 JUTA",
        "04. KECIL - > Rp 350 JUTA S/D Rp 500 JUTA",
        "05. KECIL - > Rp 500 JUTA S/D Rp 1 M",
    ],
    "MEDIUM": [
        "10. RITKOM -> Rp. 5 M S/D 15 M",
        "11. RITKOM -> Rp. 15 M S/D 25 M",
        "(PRT) 05. RITKOM -> Rp. 5 M S/D 15 M",
        "(PRT) 06. RITKOM -> Rp. 15 M S/D 25 M",
    ],
    "KUR": [
        "10. KUR Ritel 2015 New",
    ]
}

def get_segment_annotation():
    """
    Returns a Case expression to annotate the segment based on the description field.
    """
    whens = []
    for segment, descriptions in SEGMENT_MAPPING.items():
        for desc in descriptions:
            whens.append(When(description=desc, then=Value(segment)))
    
    return Case(
        *whens,
        default=Value('OTHER'),
        output_field=CharField()
    )
