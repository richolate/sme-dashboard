from django.db.models import Case, When, Value, CharField

# ─── Code-based mapping (for future data that provides product codes) ──────────
# Actual data in production uses description-based mapping below.
SEGMENT_MAPPING_BY_CODE = {
    "MEDIUM":    ["42210", "42211", "43210", "43211"],
    "SMALL NCC": ["43206", "43207", "43208", "43209", "82201", "82202", "82203",
                  "42203", "82204", "42204", "82205", "42205", "42206", "42207",
                  "42208", "42209", "80064"],
    "CC":  ["42110", "42120", "42140"],
    "KUR": ["80065"],
}

# ─── Description-based mapping (matches actual data in production DB) ──────────
# Each description value maps to exactly one segment.
# SMALL NCC = all RITKOM/KECIL loans ≤ 5 M that are NOT CC/KUR/MEDIUM.
# SMALL is the default catch-all (handled in get_segment_annotation default).
SEGMENT_MAPPING_BY_DESCRIPTION = {
    "MEDIUM": [
        "10. RITKOM -> Rp. 5 M S/D 15 M",
        "11. RITKOM -> Rp. 15 M S/D 25 M",
        "(PRT) 05. RITKOM -> Rp. 5 M S/D 15 M",
        "(PRT) 06. RITKOM -> Rp. 15 M S/D 25 M",
    ],
    "CC": [
        "RITKOM - CASHCOL RITEL (> Rp 1 M S/D Rp 25 M)",
        "RITKOM - CASHCOL MENENGAH (> Rp 25 M S/D Rp 200 M)",
        "RITKOM - CASHCOL KECIL (S/D Rp 1 M)",
    ],
    "KUR": [
        "10. KUR Ritel 2015 New",
    ],
    "SMALL NCC": [
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
    ],
}

# ─── Legacy flat mapping (kept for reference) ──────────────────────────────────
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
    ],
}


def get_segment_annotation():
    """
    Annotates each record with its segment using a two-tier lookup:

    1. Code field (SEGMENT_MAPPING_BY_CODE) — for data that carries a proper product
       code (kode jenis kredit).  Both clean ("42210") and float-format ("42210.0")
       variants are matched to handle older uploads.

    2. Description field (SEGMENT_MAPPING_BY_DESCRIPTION) — for production data whose
       code field contains internal codes that don't match the product-code mapping.
       All 25 distinct description values found in the DB are covered.

    Segment hierarchy:
        MEDIUM    — RITKOM 5M–25M
        CC        — CashCol (Cashcol Ritel / Menengah / Kecil)
        KUR       — KUR Ritel
        SMALL NCC — RITKOM/KECIL ≤ 5M (Non-CC, Non-KUR)
        SMALL     — default (catches everything not matched above;
                    also used as the aggregate of SMALL NCC + CC + KUR in queries
                    via exclude(segment='MEDIUM'))
    """
    whens = []

    # Tier 1: product code field
    for segment, codes in SEGMENT_MAPPING_BY_CODE.items():
        for code in codes:
            whens.append(When(code=code, then=Value(segment)))
            whens.append(When(code=f"{code}.0", then=Value(segment)))

    # Tier 2: description field (current production data)
    for segment, descriptions in SEGMENT_MAPPING_BY_DESCRIPTION.items():
        for desc in descriptions:
            whens.append(When(description=desc, then=Value(segment)))

    return Case(
        *whens,
        default=Value('SMALL'),
        output_field=CharField()
    )


def get_segment_annotation_legacy():
    """Legacy: description-based only, 'OTHER' default. Kept for reference."""
    whens = []
    for segment, descriptions in SEGMENT_MAPPING.items():
        for desc in descriptions:
            whens.append(When(description=desc, then=Value(segment)))
    return Case(*whens, default=Value('OTHER'), output_field=CharField())
