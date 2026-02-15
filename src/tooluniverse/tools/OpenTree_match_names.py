"""
OpenTree_match_names

Resolve species names to OTT IDs via TNRS...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OpenTree_match_names(
    names: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Resolve species names to OTT IDs via TNRS...
    """
    return get_shared_client().run_one_function(
        {
            "name": "OpenTree_match_names",
            "arguments": {"names": names},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenTree_match_names"]
