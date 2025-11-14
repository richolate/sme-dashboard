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
    {
        "key": "grafik-harian",
        "label": "Grafik Harian",
        "icon": "fas fa-chart-line",
        "url_name": "dashboard:dashboard_grafik_harian",
    },
]


METRIC_GROUPS = [
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
        "label": "Medium",
        "icon": "fas fa-briefcase",
        "pages": [
            {
                "slug": "medium-os",
                "title": "OS Medium",
                "tables": [
                    "OS MEDIUM KANCA KONSOL",
                    "OS MEDIUM KANCA ONLY",
                    "OS MEDIUM KCP ONLY",
                ],
            },
            {
                "slug": "medium-sml",
                "title": "SML Medium",
                "tables": [
                    "SML MEDIUM KANCA KONSOL",
                    "SML MEDIUM KANCA ONLY",
                    "SML MEDIUM KCP ONLY",
                ],
            },
            {
                "slug": "medium-npl",
                "title": "NPL Medium",
                "tables": [
                    "NPL MEDIUM KANCA KONSOL",
                    "NPL MEDIUM KANCA ONLY",
                    "NPL MEDIUM KCP ONLY",
                ],
            },
            {
                "slug": "medium-nsb",
                "title": "NSB Medium",
                "tables": [
                    "NSB MEDIUM KANCA KONSOL",
                    "NSB MEDIUM KANCA ONLY",
                    "NSB MEDIUM KCP ONLY",
                ],
            },
            {
                "slug": "medium-lr",
                "title": "LR Medium",
                "tables": [
                    "LR MEDIUM KANCA KONSOL",
                    "LR MEDIUM KANCA ONLY",
                    "LR MEDIUM KCP ONLY",
                ],
            },
        ],
    },
    {
        "key": "small",
        "label": "Small",
        "icon": "fas fa-chart-area",
        "pages": [
            {
                "slug": "small-os",
                "title": "OS Small",
                "tables": [
                    "TOTAL OS SMALL KANCA KONSOL",
                    "TOTAL OS SMALL KANCA ONLY",
                    "TOTAL OS SMALL KCP ONLY",
                ],
            },
            {
                "slug": "small-sml",
                "title": "SML Small",
                "tables": [
                    "TOTAL SML SMALL KANCA KONSOL",
                    "TOTAL SML SMALL KANCA ONLY",
                    "TOTAL SML SMALL KCP ONLY",
                ],
            },
            {
                "slug": "small-npl",
                "title": "NPL Small",
                "tables": [
                    "TOTAL NPL SMALL KANCA KONSOL",
                    "TOTAL NPL SMALL KANCA ONLY",
                    "TOTAL NPL SMALL KCP ONLY",
                ],
            },
            {
                "slug": "small-nsb",
                "title": "NSB Small",
                "tables": [
                    "TOTAL NASABAH SMALL KANCA KONSOL",
                    "TOTAL NASABAH SMALL KANCA ONLY",
                    "TOTAL NASABAH SMALL KCP ONLY",
                ],
            },
            {
                "slug": "small-lr",
                "title": "LR Small",
                "tables": [
                    "TOTAL LR SMALL KANCA KONSOL",
                    "TOTAL LR SMALL KANCA ONLY",
                    "TOTAL LR SMALL KCP ONLY",
                ],
            },
            {
                "slug": "small-lar",
                "title": "LAR Small",
                "tables": [
                    "TOTAL LAR SMALL KANCA KONSOL",
                    "TOTAL LAR SMALL KANCA ONLY",
                    "TOTAL LAR SMALL KCP ONLY",
                ],
            },
        ],
    },
    {
        "key": "small-ncc",
        "label": "Small NCC",
        "icon": "fas fa-chart-line",
        "pages": [
            {
                "slug": "small-ncc-os",
                "title": "OS Small NCC",
                "tables": [
                    "OS SMALL SD 5M KANCA KONSOL",
                    "OS SMALL SD 5M KANCA ONLY",
                    "OS SMALL SD 5M KCP ONLY",
                ],
            },
            {
                "slug": "small-ncc-sml",
                "title": "SML Small NCC",
                "tables": [
                    "SML SMALL SD 5M KANCA KONSOL",
                    "SML SMALL SD 5M KANCA ONLY",
                    "SML SMALL SD 5M KCP ONLY",
                ],
            },
            {
                "slug": "small-ncc-npl",
                "title": "NPL Small NCC",
                "tables": [
                    "NPL SMALL SD 5M KANCA KONSOL",
                    "NPL SMALL SD 5M KANCA ONLY",
                    "NPL SMALL SD 5M KCP ONLY",
                ],
            },
            {
                "slug": "small-ncc-nsb",
                "title": "NSB Small NCC",
                "tables": [
                    "NASABAH SMALL SD 5M KANCA KONSOL",
                    "NASABAH SMALL SD 5M KANCA ONLY",
                    "NASABAH SMALL SD 5M KCP ONLY",
                ],
            },
            {
                "slug": "small-ncc-lr",
                "title": "LR Small NCC",
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
                "slug": "cc-sml",
                "title": "SML CC",
                "tables": [
                    "SML CC KANCA KONSOL",
                    "SML CC KANCA ONLY",
                    "SML CC KCP ONLY",
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
                "slug": "kur-sml",
                "title": "SML KUR",
                "tables": [
                    "SML KUR KANCA KONSOL",
                    "SML KUR KANCA ONLY",
                    "SML KUR KCP ONLY",
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
