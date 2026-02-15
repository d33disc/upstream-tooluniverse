"""
OpenTree_get_taxon

Get taxonomy info for an OTT ID...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OpenTree_get_taxon(
    ott_id: int,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get taxonomy info for an OTT ID...
    """
    return get_shared_client().run_one_function(
        {
            "name": "OpenTree_get_taxon",
            "arguments": {"ott_id": ott_id},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenTree_get_taxon"]
