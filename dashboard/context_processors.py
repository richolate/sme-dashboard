"""Context processors for the dashboard app."""

from typing import Any, Dict

from .navigation import build_menu


def navigation_context(request) -> Dict[str, Any]:
    """Inject sidebar navigation metadata into all templates."""

    resolver_match = getattr(request, "resolver_match", None)
    current_slug = None
    current_url_name = None
    if resolver_match:
        current_url_name = resolver_match.url_name
        current_slug = resolver_match.kwargs.get("slug")

    menu = []
    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        menu = build_menu(
            current_slug=current_slug,
            current_url_name=current_url_name,
            user=user,
        )

    return {
        "dashboard_menu": menu,
        "current_menu_slug": current_slug,
        "current_menu_url_name": current_url_name,
    }
