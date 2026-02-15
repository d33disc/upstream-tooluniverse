"""
iNaturalist_get_species_counts

Get species observation counts...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def iNaturalist_get_species_counts(
    taxon_id: int = None,
    place_id: int = None,
    quality_grade: str = None,
    per_page: int = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get species observation counts...
    """
    return get_shared_client().run_one_function(
        {
            "name": "iNaturalist_get_species_counts",
            "arguments": {
                "taxon_id": taxon_id,
                "place_id": place_id,
                "quality_grade": quality_grade,
                "per_page": per_page,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["iNaturalist_get_species_counts"]
