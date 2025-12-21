from __future__ import annotations

"""Navigation and metric page definitions for the dashboard application."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from django.urls import reverse
from django.utils.text import slugify


@dataclass(frozen=True)
class MetricPage:
    slug: str
    title: str
    section: str
    tables: List[str]
    description: str = ""


TOP_LEVEL_LINKS = [
    {
        "key": "home",
        "label": "Dashboard Utama",
        "icon": "fas fa-home",
        "url_name": "dashboard:home",
    },
]


METRIC_GROUPS = [
    {
        "key": "timeseries",
        "label": "Timeseries",
        "icon": "fas fa-chart-line",
        "pages": [
            {
                "slug": "timeseries-bulanan",
                "title": "Timeseries Bulanan",
                "tables": [],
                "description": "Visualisasi tren bulanan untuk metrik utama.",
            },
            {
                "slug": "timeseries-baki-debit-uker",
                "title": "Timeseries Baki Debit UKER",
                "tables": [],
                "description": "Pergerakan baki debet per UKER secara historis.",
            },
            {
                "slug": "timeseries-os",
                "title": "Timeseries OS",
                "tables": [],
                "description": "Timeseries outstanding loan secara keseluruhan.",
            },
            {
                "slug": "timeseries-os-dpk-npl-lar",
                "title": "Timeseries OS DPK NPL LAR",
                "tables": [],
                "description": "Gabungan OS, DPK, NPL, dan LAR dalam satu rangkaian waktu.",
            },
            {
                "slug": "timeseries-harian",
                "title": "Timeseries Harian",
                "tables": [],
                "description": "Detail timeseries harian untuk monitoring cepat.",
            },
        ],
    },
    {
        "key": "summary",
        "label": "Summary",
        "icon": "fas fa-layer-group",
        "pages": [
            {
                "slug": "summary-medium-only",
                "title": "Summary Medium Only",
                "tables": [],
                "description": "Halaman ringkas untuk menampilkan highlight segmen medium only.",
            },
            {
                "slug": "summary-konsol",
                "title": "Summary Konsol",
                "tables": [],
                "description": "Placeholder untuk ringkasan konsolidasi seluruh segmen.",
            },
            {
                "slug": "summary-only",
                "title": "Summary Only",
                "tables": [],
                "description": "Gunakan halaman ini untuk highlight summary only sesuai kebutuhan bisnis.",
            },
        ],
    },
    {
        "key": "medium",
        "label": "MEDIUM",
        "icon": "fas fa-briefcase",
        "color": "#00b050",
        "pages": [
            {
                "slug": "medium-os",
                "title": "OS MEDIUM",
                "tables": [
                    "OS MEDIUM KANCA KONSOL",
                ],
            },
            {
                "slug": "medium-dpk",
                "title": "DPK MEDIUM",
                "tables": [
                    "DPK MEDIUM KANCA KONSOL",
                ],
            },
            {
                "slug": "medium-npl",
                "title": "NPL MEDIUM",
                "tables": [
                    "NPL MEDIUM KANCA KONSOL",
                ],
            },
            {
                "slug": "medium-nsb",
                "title": "NSB MEDIUM",
                "tables": [
                    "NSB MEDIUM KANCA KONSOL",
                ],
            },
            {
                "slug": "medium-lr",
                "title": "LR MEDIUM",
                "tables": [
                    "LR MEDIUM KANCA KONSOL",
                ],
            },
        ],
    },
    {
        "key": "small",
        "label": "SMALL",
        "icon": "fas fa-chart-area",
        "color": "#31869b",
        "pages": [
            {
                "slug": "small-os",
                "title": "OS SMALL",
                "tables": [
                    "TOTAL OS SMALL KANCA KONSOL",
                    "TOTAL OS SMALL KANCA ONLY",
                    "TOTAL OS SMALL KCP ONLY",
                ],
            },
            {
                "slug": "small-dpk",
                "title": "DPK SMALL",
                "tables": [
                    "TOTAL DPK SMALL KANCA KONSOL",
                    "TOTAL DPK SMALL KANCA ONLY",
                    "TOTAL DPK SMALL KCP ONLY",
                ],
            },
            {
                "slug": "small-dpk-pct",
                "title": "%DPK SMALL",
                "tables": [
                    "TOTAL %DPK SMALL KANCA KONSOL",
                    "TOTAL %DPK SMALL KANCA ONLY",
                    "TOTAL %DPK SMALL KCP ONLY",
                ],
            },
            {
                "slug": "small-npl",
                "title": "NPL SMALL",
                "tables": [
                    "TOTAL NPL SMALL KANCA KONSOL",
                    "TOTAL NPL SMALL KANCA ONLY",
                    "TOTAL NPL SMALL KCP ONLY",
                ],
            },
            {
                "slug": "small-npl-pct",
                "title": "%NPL SMALL",
                "tables": [
                    "TOTAL %NPL SMALL KANCA KONSOL",
                    "TOTAL %NPL SMALL KANCA ONLY",
                    "TOTAL %NPL SMALL KCP ONLY",
                ],
            },
            {
                "slug": "small-lar",
                "title": "LAR SMALL",
                "tables": [
                    "TOTAL LAR SMALL KANCA KONSOL",
                    "TOTAL LAR SMALL KANCA ONLY",
                    "TOTAL LAR SMALL KCP ONLY",
                ],
            },
            {
                "slug": "small-nsb",
                "title": "NSB SMALL",
                "tables": [
                    "TOTAL NASABAH SMALL KANCA KONSOL",
                    "TOTAL NASABAH SMALL KANCA ONLY",
                    "TOTAL NASABAH SMALL KCP ONLY",
                ],
            },
            {
                "slug": "small-lr",
                "title": "LR SMALL",
                "tables": [
                    "TOTAL LR SMALL KANCA KONSOL",
                    "TOTAL LR SMALL KANCA ONLY",
                    "TOTAL LR SMALL KCP ONLY",
                ],
            },
        ],
    },
    {
        "key": "small-ncc",
        "label": "SMALL NCC",
        "icon": "fas fa-chart-line",
        "color": "#ff0000",
        "pages": [
            {
                "slug": "small-ncc-os",
                "title": "OS SMALL NCC",
                "tables": [
                    "OS SMALL SD 5M KANCA KONSOL",
                    "OS SMALL SD 5M KANCA ONLY",
                    "OS SMALL SD 5M KCP ONLY",
                ],
            },
            {
                "slug": "small-ncc-dpk",
                "title": "DPK SMALL NCC",
                "tables": [
                    "DPK SMALL SD 5M KANCA KONSOL",
                    "DPK SMALL SD 5M KANCA ONLY",
                    "DPK SMALL SD 5M KCP ONLY",
                ],
            },
            {
                "slug": "small-ncc-npl",
                "title": "NPL SMALL NCC",
                "tables": [
                    "NPL SMALL SD 5M KANCA KONSOL",
                    "NPL SMALL SD 5M KANCA ONLY",
                    "NPL SMALL SD 5M KCP ONLY",
                ],
            },
            {
                "slug": "small-ncc-nsb",
                "title": "NSB SMALL NCC",
                "tables": [
                    "NASABAH SMALL SD 5M KANCA KONSOL",
                    "NASABAH SMALL SD 5M KANCA ONLY",
                    "NASABAH SMALL SD 5M KCP ONLY",
                ],
            },
            {
                "slug": "small-ncc-lr",
                "title": "LR SMALL NCC",
                "tables": [
                    "LR SMALL SD 5M KANCA KONSOL",
                    "LR SMALL SD 5M KANCA ONLY",
                    "LR SMALL SD 5M KCP ONLY",
                ],
            },
        ],
    },
    {
        "key": "cc",
        "label": "CC",
        "icon": "fas fa-credit-card",
        "color": "#ffff00",
        "pages": [
            {
                "slug": "cc-os",
                "title": "OS CC",
                "tables": [
                    "OS CC KANCA KONSOL",
                    "OS CC KANCA ONLY",
                    "OS CC KCP ONLY",
                ],
            },
            {
                "slug": "cc-dpk",
                "title": "DPK CC",
                "tables": [
                    "DPK CC KANCA KONSOL",
                    "DPK CC KANCA ONLY",
                    "DPK CC KCP ONLY",
                ],
            },
            {
                "slug": "cc-npl",
                "title": "NPL CC",
                "tables": [
                    "NPL CC KANCA KONSOL",
                    "NPL CC KANCA ONLY",
                    "NPL CC KCP ONLY",
                ],
            },
            {
                "slug": "cc-nsb",
                "title": "NSB CC",
                "tables": [
                    "NASABAH CC KANCA KONSOL",
                    "NASABAH CC KANCA ONLY",
                    "NASABAH CC KCP ONLY",
                ],
            },
        ],
    },
    {
        "key": "kur",
        "label": "KUR",
        "icon": "fas fa-hand-holding-usd",
        "color": "#c0504d",
        "pages": [
            {
                "slug": "kur-os",
                "title": "OS KUR",
                "tables": [
                    "OS KUR KANCA KONSOL",
                    "OS KUR KANCA ONLY",
                    "OS KUR KCP ONLY",
                ],
            },
            {
                "slug": "kur-dpk",
                "title": "DPK KUR",
                "tables": [
                    "DPK KUR KANCA KONSOL",
                    "DPK KUR KANCA ONLY",
                    "DPK KUR KCP ONLY",
                ],
            },
            {
                "slug": "kur-npl",
                "title": "NPL KUR",
                "tables": [
                    "NPL KUR KANCA KONSOL",
                    "NPL KUR KANCA ONLY",
                    "NPL KUR KCP ONLY",
                ],
            },
            {
                "slug": "kur-nsb",
                "title": "NSB KUR",
                "tables": [
                    "NASABAH KUR KANCA KONSOL",
                    "NASABAH KUR KANCA ONLY",
                    "NASABAH KUR KCP ONLY",
                ],
            },
            {
                "slug": "kur-lr",
                "title": "LR KUR",
                "tables": [
                    "LR KUR KANCA KONSOL",
                    "LR KUR KANCA ONLY",
                    "LR KUR KCP ONLY",
                ],
            },
        ],
    },
]

DATA_MANAGEMENT_CHILDREN = [
    {
        "key": "view-all-data",
        "label": "View All Data",
        "url_name": "data_management:view_all_data",
        "requires_admin": True,
    },
    {
        "key": "upload-data",
        "label": "Upload Data",
        "url_name": "data_management:upload_data",
        "requires_admin": True,
    },
    {
        "key": "delete-data",
        "label": "Delete Data",
        "url_name": "data_management:delete_data",
        "requires_admin": True,
    },
    {
        "key": "history-data",
        "label": "History Data",
        "url_name": "data_management:upload_history",
        "requires_admin": True,
    },
]


METRIC_PAGES: Dict[str, MetricPage] = {}
for group in METRIC_GROUPS:
    for page in group["pages"]:
        slug = page["slug"]
        METRIC_PAGES[slug] = MetricPage(
            slug=slug,
            title=page["title"],
            section=group["label"],
            tables=page.get("tables", []),
            description=page.get("description", ""),
        )


def build_menu(
    *,
    current_slug: Optional[str],
    current_url_name: Optional[str],
    user,
) -> List[Dict[str, Any]]:
    """Build sidebar menu structure with active states."""

    menu: List[Dict[str, Any]] = []
    user_is_admin = False
    if getattr(user, "is_authenticated", False):
        is_admin_callable = getattr(user, "is_admin", None)
        if callable(is_admin_callable):
            user_is_admin = bool(is_admin_callable())

    # Top-level links
    for link in TOP_LEVEL_LINKS:
        url = reverse(link["url_name"])
        menu.append(
            {
                "key": link["key"],
                "label": link["label"],
                "icon": link.get("icon", "fas fa-circle"),
                "url": url,
                "active": current_url_name == link["url_name"],
                "children": [],
                "collapse_id": "",
            }
        )

    # Metric groups
    for group in METRIC_GROUPS:
        children = []
        for page in group["pages"]:
            slug = page["slug"]
            url = reverse("dashboard:metric_page", kwargs={"slug": slug})
            children.append(
                {
                    "key": slug,
                    "label": page["title"],
                    "url": url,
                    "active": slug == current_slug,
                }
            )
        collapse_id = f"menu-{slugify(group['key'])}"
        is_open = any(child["active"] for child in children)
        menu.append(
            {
                "key": group["key"],
                "label": group["label"],
                "icon": group.get("icon", "fas fa-folder"),
                "url": "#",
                "children": children,
                "collapse_id": collapse_id,
                "open": is_open,
                "active": is_open,
                "color": group.get("color", ""),
            }
        )

    # Data Management group
    data_children = []
    for child in DATA_MANAGEMENT_CHILDREN:
        if child.get("requires_admin") and not user_is_admin:
            continue
        url = reverse(child["url_name"])
        data_children.append(
            {
                "key": child["key"],
                "label": child["label"],
                "url": url,
                "active": current_url_name == child["url_name"],
            }
        )

    if data_children:
        collapse_id = "menu-data-management"
        is_open = any(child["active"] for child in data_children)
        menu.append(
            {
                "key": "data-management",
                "label": "Data Management",
                "icon": "fas fa-database",
                "url": "#",
                "children": data_children,
                "collapse_id": collapse_id,
                "open": is_open,
                "active": is_open,
            }
        )

    return menu


__all__ = ["METRIC_PAGES", "build_menu"]
