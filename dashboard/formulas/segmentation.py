from django.db.models import Case, When, Value, CharField

# Mapping berdasarkan CODE (kolom pertama di gambar)
SEGMENT_MAPPING_BY_CODE = {
    "MEDIUM": [
        "42210",  # 10. RITKOM -> Rp. 5 M S/D 15 M
        "42211",  # 11. RITKOM -> Rp. 15 M S/D 25 M
        "43210",  # (PRT) 05. RITKOM -> Rp. 5 M S/D 15 M
        "43211",  # (PRT) 06. RITKOM -> Rp. 15 M S/D 25 M
    ],
    "SMALL": [
        "43206",  # (PRT) 01. RITKOM - > Rp 1 M S/D Rp 2 M
        "43207",  # (PRT) 02. RITKOM - > Rp 2 M S/D Rp 3 M
        "43208",  # (PRT) 03. RITKOM - > Rp 3 M S/D Rp 4 M
        "43209",  # (PRT) 04. RITKOM - > Rp 4 M S/D Rp 5 M
        "82201",  # 01. KECIL - S/D Rp 50 JUTA
        "82202",  # 02. KECIL - > Rp.50 JUTA S/D Rp 100 JUTA
        "82203",  # 03. KECIL - > Rp 100 JUTA S/D Rp 350 JUTA
        "42203",  # 03. RITKOM - > Rp 100 JUTA S/D Rp 350 JUTA
        "82204",  # 04. KECIL - > Rp 350 JUTA S/D Rp 500 JUTA
        "42204",  # 04. RITKOM - > Rp 350 JUTA S/D Rp 500 JUTA
        "82205",  # 05. KECIL - > Rp 500 JUTA S/D Rp 1 M
        "42205",  # 05. RITKOM - > Rp 500 JUTA S/D Rp 1 M
        "42206",  # 06. RITKOM - > Rp 1 M S/D Rp 2 M
        "42207",  # 07. RITKOM - > Rp 2 M S/D Rp 3 M
        "42208",  # 08. RITKOM - > Rp 3 M S/D Rp 4 M
        "42209",  # 09. RITKOM - > Rp 4 M S/D Rp 5 M
        "80064",  # KREDIT PANGAN
        "42110",  # RITKOM - CASHCOL RITEL (> Rp 1 M S/D Rp 25 M)
        "42120",  # RITKOM - CASHCOL MENENGAH (> Rp 25 M S/D Rp 200 M)
        "42140",  # RITKOM - CASHCOL KECIL (S/D Rp 1 M)
        "80065",  # 10. KUR Ritel 2015 New
    ],
    "SMALL NCC": [
        "43206",  # (PRT) 01. RITKOM - > Rp 1 M S/D Rp 2 M
        "43207",  # (PRT) 02. RITKOM - > Rp 2 M S/D Rp 3 M
        "43208",  # (PRT) 03. RITKOM - > Rp 3 M S/D Rp 4 M
        "43209",  # (PRT) 04. RITKOM - > Rp 4 M S/D Rp 5 M
        "82201",  # 01. KECIL - S/D Rp 50 JUTA
        "82202",  # 02. KECIL - > Rp.50 JUTA S/D Rp 100 JUTA
        "82203",  # 03. KECIL - > Rp 100 JUTA S/D Rp 350 JUTA
        "42203",  # 03. RITKOM - > Rp 100 JUTA S/D Rp 350 JUTA
        "82204",  # 04. KECIL - > Rp 350 JUTA S/D Rp 500 JUTA
        "42204",  # 04. RITKOM - > Rp 350 JUTA S/D Rp 500 JUTA
        "82205",  # 05. KECIL - > Rp 500 JUTA S/D Rp 1 M
        "42205",  # 05. RITKOM - > Rp 500 JUTA S/D Rp 1 M
        "42206",  # 06. RITKOM - > Rp 1 M S/D Rp 2 M
        "42207",  # 07. RITKOM - > Rp 2 M S/D Rp 3 M
        "42208",  # 08. RITKOM - > Rp 3 M S/D Rp 4 M
        "42209",  # 09. RITKOM - > Rp 4 M S/D Rp 5 M
        "80064",  # KREDIT PANGAN
    ],
    "CC": [
        "42110",  # RITKOM - CASHCOL RITEL (> Rp 1 M S/D Rp 25 M)
        "42120",  # RITKOM - CASHCOL MENENGAH (> Rp 25 M S/D Rp 200 M)
        "42140",  # RITKOM - CASHCOL KECIL (S/D Rp 1 M)
    ],
    "KUR": [
        "80065",  # 10. KUR Ritel 2015 New
    ]
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
