"""
iNaturalist_search_taxa

Search iNaturalist taxa by name...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def iNaturalist_search_taxa(
    query: str,
    per_page: int = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search iNaturalist taxa by name...
    """
    return get_shared_client().run_one_function(
        {
            "name": "iNaturalist_search_taxa",
            "arguments": {"query": query, "per_page": per_page},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["iNaturalist_search_taxa"]
