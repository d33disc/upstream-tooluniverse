"""
iNaturalist_get_taxon

Get taxon details by iNaturalist ID...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def iNaturalist_get_taxon(
    taxon_id: int,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get taxon details by iNaturalist ID...
    """
    return get_shared_client().run_one_function(
        {
            "name": "iNaturalist_get_taxon",
            "arguments": {"taxon_id": taxon_id},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["iNaturalist_get_taxon"]
