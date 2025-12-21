"""
Script untuk generate replacement strings untuk metric_page.html
Mengubah logic warna dan format persen
"""

# Pattern lama untuk percentage cells (rows)
old_patterns_rows = [
    '<td class="{% if row.DtD_pct >= 0 %}bg-positive{% else %}bg-negative{% endif %}">{{ row.DtD_pct|floatformat:2 }}%</td>',
    '<td class="{% if row.MoM_pct >= 0 %}bg-positive{% else %}bg-negative{% endif %}">{{ row.MoM_pct|floatformat:2 }}%</td>',
    '<td class="{% if row.MtD_pct >= 0 %}bg-positive{% else %}bg-negative{% endif %}">{{ row.MtD_pct|floatformat:2 }}%</td>',
    '<td class="{% if row.YtD_pct >= 0 %}bg-positive{% else %}bg-negative{% endif %}">{{ row.YtD_pct|floatformat:2 }}%</td>',
]

# Pattern baru untuk percentage cells (rows) - dengan inverse color logic untuk DPK/NPL/LAR/LR
new_patterns_rows = [
    '<td class="{% if metric_type in "dpk,npl,lar,lr" %}{% if row.DtD_pct >= 0 %}bg-negative{% else %}bg-positive{% endif %}{% else %}{% if row.DtD_pct >= 0 %}bg-positive{% else %}bg-negative{% endif %}{% endif %}">{{ row.DtD_pct|floatformat:1 }}%</td>',
    '<td class="{% if metric_type in "dpk,npl,lar,lr" %}{% if row.MoM_pct >= 0 %}bg-negative{% else %}bg-positive{% endif %}{% else %}{% if row.MoM_pct >= 0 %}bg-positive{% else %}bg-negative{% endif %}{% endif %}">{{ row.MoM_pct|floatformat:1 }}%</td>',
    '<td class="{% if metric_type in "dpk,npl,lar,lr" %}{% if row.MtD_pct >= 0 %}bg-negative{% else %}bg-positive{% endif %}{% else %}{% if row.MtD_pct >= 0 %}bg-positive{% else %}bg-negative{% endif %}{% endif %}">{{ row.MtD_pct|floatformat:1 }}%</td>',
    '<td class="{% if metric_type in "dpk,npl,lar,lr" %}{% if row.YtD_pct >= 0 %}bg-negative{% else %}bg-positive{% endif %}{% else %}{% if row.YtD_pct >= 0 %}bg-positive{% else %}bg-negative{% endif %}{% endif %}">{{ row.YtD_pct|floatformat:1 }}%</td>',
]

# Pattern lama untuk percentage cells (totals)
old_patterns_totals = [
    '<td class="{% if tables.konsol.totals.DtD_pct >= 0 %}bg-positive{% else %}bg-negative{% endif %}"><strong>{{ tables.konsol.totals.DtD_pct|floatformat:2 }}%</strong></td>',
    '<td class="{% if tables.konsol.totals.MoM_pct >= 0 %}bg-positive{% else %}bg-negative{% endif %}"><strong>{{ tables.konsol.totals.MoM_pct|floatformat:2 }}%</strong></td>',
    '<td class="{% if tables.konsol.totals.MtD_pct >= 0 %}bg-positive{% else %}bg-negative{% endif %}"><strong>{{ tables.konsol.totals.MtD_pct|floatformat:2 }}%</strong></td>',
    '<td class="{% if tables.konsol.totals.YtD_pct >= 0 %}bg-positive{% else %}bg-negative{% endif %}"><strong>{{ tables.konsol.totals.YtD_pct|floatformat:2 }}%</strong></td>',
]

new_patterns_totals = [
    '<td class="{% if metric_type in "dpk,npl,lar,lr" %}{% if tables.konsol.totals.DtD_pct >= 0 %}bg-negative{% else %}bg-positive{% endif %}{% else %}{% if tables.konsol.totals.DtD_pct >= 0 %}bg-positive{% else %}bg-negative{% endif %}{% endif %}"><strong>{{ tables.konsol.totals.DtD_pct|floatformat:1 }}%</strong></td>',
    '<td class="{% if metric_type in "dpk,npl,lar,lr" %}{% if tables.konsol.totals.MoM_pct >= 0 %}bg-negative{% else %}bg-positive{% endif %}{% else %}{% if tables.konsol.totals.MoM_pct >= 0 %}bg-positive{% else %}bg-negative{% endif %}{% endif %}"><strong>{{ tables.konsol.totals.MoM_pct|floatformat:1 }}%</strong></td>',
    '<td class="{% if metric_type in "dpk,npl,lar,lr" %}{% if tables.konsol.totals.MtD_pct >= 0 %}bg-negative{% else %}bg-positive{% endif %}{% else %}{% if tables.konsol.totals.MtD_pct >= 0 %}bg-positive{% else %}bg-negative{% endif %}{% endif %}"><strong>{{ tables.konsol.totals.MtD_pct|floatformat:1 }}%</strong></td>',
    '<td class="{% if metric_type in "dpk,npl,lar,lr" %}{% if tables.konsol.totals.YtD_pct >= 0 %}bg-negative{% else %}bg-positive{% endif %}{% else %}{% if tables.konsol.totals.YtD_pct >= 0 %}bg-positive{% else %}bg-negative{% endif %}{% endif %}"><strong>{{ tables.konsol.totals.YtD_pct|floatformat:1 }}%</strong></td>',
]

# Patterns untuk tables.kanca dan tables.kcp (similar pattern)
old_patterns_kanca_rows = [old.replace('tables.konsol', 'tables.kanca') for old in old_patterns_totals]
new_patterns_kanca_rows = [new.replace('tables.konsol', 'tables.kanca') for new in new_patterns_totals]

old_patterns_kcp_rows = [old.replace('tables.konsol', 'tables.kcp') for old in old_patterns_totals]
new_patterns_kcp_rows = [new.replace('tables.konsol', 'tables.kcp') for new in new_patterns_totals]

print("=" * 80)
print("REPLACEMENT PATTERNS GENERATED")
print("=" * 80)
print("\nTotal patterns to replace:")
print(f"- Row percentage cells: {len(old_patterns_rows)}")
print(f"- Konsol total cells: {len(old_patterns_totals)}")
print(f"- Kanca total cells: {len(old_patterns_kanca_rows)}")
print(f"- KCP total cells: {len(old_patterns_kcp_rows)}")
print(f"Total: {len(old_patterns_rows) + len(old_patterns_totals) + len(old_patterns_kanca_rows) + len(old_patterns_kcp_rows)}")

print("\n" + "=" * 80)
print("LOGIC EXPLANATION")
print("=" * 80)
print("""
OLD LOGIC (OS SMALL):
- Plus (+) value → GREEN (bg-positive)
- Minus (-) value → RED (bg-negative)

NEW LOGIC (DPK/NPL/LAR/LR SMALL):
- Plus (+) value → RED (bg-negative)  ← INVERSE!
- Minus (-) value → GREEN (bg-positive) ← INVERSE!

IMPLEMENTATION:
{% if metric_type in "dpk,npl,lar,lr" %}
    <!-- Inverse color logic -->
    {% if value >= 0 %}bg-negative{% else %}bg-positive{% endif %}
{% else %}
    <!-- Normal color logic -->
    {% if value >= 0 %}bg-positive{% else %}bg-negative{% endif %}
{% endif %}

FORMAT CHANGE:
- OLD: floatformat:2 (e.g., 5.25%)
- NEW: floatformat:1 (e.g., 5.3%)
""")

print("=" * 80)
