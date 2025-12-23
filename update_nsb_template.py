"""
Script untuk update template metric_page.html 
Menambahkan conditional format_integer untuk NSB metric
"""

import re

template_path = r"e:\BRI\Performance Highlight SME Dashboard\templates\dashboard\metric_page.html"

# Read template
with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern untuk kolom posisi (A, B, C, D, E) - KANCA rows
# Old: {{ row.A|format_number:0|default:"-" }}
# New: {% if metric_type == 'nsb' %}{{ row.A|format_integer:0|default:"-" }}{% else %}{{ row.A|format_number:0|default:"-" }}{% endif %}

position_columns = ['A', 'B', 'C', 'D', 'E']
change_columns = ['DtD', 'MoM', 'MtD', 'YtD']

# Update KANCA rows
for col in position_columns:
    old_pattern = f'{{{{ row.{col}\\|format_number:0\\|default:"-" }}}}'
    new_replacement = f'{{% if metric_type == \'nsb\' %}}{{{{ row.{col}|format_integer:0|default:"-" }}}}{{% else %}}{{{{ row.{col}|format_number:0|default:"-" }}}}{{% endif %}}'
    # Only for KANCA section (after line 1650 approx)
    # We'll do manual check
    
# Update KANCA rows - change columns (with parentheses)
for col in change_columns:
    old_pattern = f'{{{{ row.{col}\\|format_number_parentheses:0\\|default:"-" }}}}'
    new_replacement = f'{{% if metric_type == \'nsb\' %}}{{{{ row.{col}|format_integer_parentheses:0|default:"-" }}}}{{% else %}}{{{{ row.{col}|format_number_parentheses:0|default:"-" }}}}{{% endif %}}'

# Update KANCA totals
for col in position_columns:
    old_pattern = f'{{{{ tables.kanca.totals.{col}\\|format_number:0 }}}}'
    new_replacement = f'{{% if metric_type == \'nsb\' %}}{{{{ tables.kanca.totals.{col}|format_integer:0 }}}}{{% else %}}{{{{ tables.kanca.totals.{col}|format_number:0 }}}}{{% endif %}}'

for col in change_columns:
    old_pattern = f'{{{{ tables.kanca.totals.{col}\\|format_number_parentheses:0 }}}}'
    new_replacement = f'{{% if metric_type == \'nsb\' %}}{{{{ tables.kanca.totals.{col}|format_integer_parentheses:0 }}}}{{% else %}}{{{{ tables.kanca.totals.{col}|format_number_parentheses:0 }}}}{{% endif %}}'

# Update KCP rows and totals similar patterns

print("Update script ready. Please run manual replacements in the file.")
print("Pattern examples:")
print("Old: {{ row.A|format_number:0|default:\"-\" }}")
print("New: {% if metric_type == 'nsb' %}{{ row.A|format_integer:0|default:\"-\" }}{% else %}{{ row.A|format_number:0|default:\"-\" }}{% endif %}")
