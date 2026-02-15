"""
iNaturalist_search_observations

Search biodiversity observations...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def iNaturalist_search_observations(
    taxon_id: int = None,
    query: str = None,
    quality_grade: str = None,
    place_id: int = None,
    per_page: int = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search biodiversity observations...
    """
    return get_shared_client().run_one_function(
        {
            "name": "iNaturalist_search_observations",
            "arguments": {
                "taxon_id": taxon_id,
                "query": query,
                "quality_grade": quality_grade,
                "place_id": place_id,
                "per_page": per_page,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["iNaturalist_search_observations"]
