"""
NCIThesaurus_get_children

Get child concepts from NCI hierarchy...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def NCIThesaurus_get_children(
    code: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get child concepts from NCI hierarchy...
    """
    return get_shared_client().run_one_function(
        {
            "name": "NCIThesaurus_get_children",
            "arguments": {"code": code},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["NCIThesaurus_get_children"]
