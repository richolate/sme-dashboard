from django.db.models import Case, When, Value, CharField

SEGMENT_MAPPING_BY_CODE = {
    "MEDIUM": ["42210", "42211", "43210", "43211"],
    "SMALL": ["43206", "43207", "43208", "43209", "82201", "82202", "82203", "42203", "82204", "42204", 
              "82205", "42205", "42206", "42207", "42208", "42209", "80064", "42110", "42120", "42140", "80065"],
    "SMALL NCC": ["43206", "43207", "43208", "43209", "82201", "82202", "82203", "42203", "82204", "42204", 
                  "82205", "42205", "42206", "42207", "42208", "42209", "80064"],
    "CC": ["42110", "42120", "42140"],
    "KUR": ["80065"]
}

# Legacy mapping for backward compatibility (if needed)
SEGMENT_MAPPING = {
    "CC": [
        "RITKOM - CASHCOL RITEL (> Rp 1 M S/D Rp 25 M)",
        "RITKOM - CASHCOL MENENGAH (> Rp 25 M S/D Rp 200 M)",
        "RITKOM - CASHCOL KECIL (S/D Rp 1 M)",
    ],
    "SMALL": [
        "(PRT) 01. RITKOM - > Rp 1 M S/D Rp 2 M",
        "(PRT) 02. RITKOM - > Rp 2 M S/D Rp 3 M",
        "(PRT) 03. RITKOM - > Rp 3 M S/D Rp 4 M",
        "(PRT) 04. RITKOM - > Rp 4 M S/D Rp 5 M",
        "01. KECIL - S/D Rp 50 JUTA",
        "02. KECIL - > Rp.50 JUTA S/D Rp 100 JUTA",
        "03. KECIL - > Rp 100 JUTA S/D Rp 350 JUTA",
        "03. RITKOM - > Rp 100 JUTA S/D Rp 350 JUTA",
        "04. KECIL - > Rp 350 JUTA S/D Rp 500 JUTA",
        "04. RITKOM - > Rp 350 JUTA S/D Rp 500 JUTA",
        "05. KECIL - > Rp 500 JUTA S/D Rp 1 M",
        "05. RITKOM - > Rp 500 JUTA S/D Rp 1 M",
        "06. RITKOM - > Rp 1 M S/D Rp 2 M",
        "07. RITKOM - > Rp 2 M S/D Rp 3 M",
        "08. RITKOM - > Rp 3 M S/D Rp 4 M",
        "09. RITKOM - > Rp 4 M S/D Rp 5 M",
        "KREDIT PANGAN",
        "RITKOM - CASHCOL RITEL (> Rp 1 M S/D Rp 25 M)",
        "RITKOM - CASHCOL MENENGAH (> Rp 25 M S/D Rp 200 M)",
        "RITKOM - CASHCOL KECIL (S/D Rp 1 M)",
        "10. KUR Ritel 2015 New",
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
    Returns a Case expression to annotate the segment based on the CODE field (kode_jenis_kredit).
    This is more reliable than using description text.
    """
    whens = []
    for segment, codes in SEGMENT_MAPPING_BY_CODE.items():
        for code in codes:
            whens.append(When(code=code, then=Value(segment)))
    
    return Case(
        *whens,
        default=Value('OTHER'),
        output_field=CharField()
    )

def get_segment_annotation_legacy():
    """
    Legacy function: Returns a Case expression to annotate the segment based on the description field.
    Use get_segment_annotation() instead for more reliable CODE-based mapping.
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
