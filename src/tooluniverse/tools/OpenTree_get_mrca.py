"""
OpenTree_get_mrca

Find MRCA of taxa by OTT IDs...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OpenTree_get_mrca(
    ott_ids: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Find MRCA of taxa by OTT IDs...
    """
    return get_shared_client().run_one_function(
        {
            "name": "OpenTree_get_mrca",
            "arguments": {"ott_ids": ott_ids},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenTree_get_mrca"]
