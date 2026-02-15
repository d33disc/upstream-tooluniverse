"""
NCIThesaurus_search

Search NCI Thesaurus for cancer concepts...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def NCIThesaurus_search(
    term: str,
    page_size: int = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search NCI Thesaurus for cancer concepts...
    """
    return get_shared_client().run_one_function(
        {
            "name": "NCIThesaurus_search",
            "arguments": {"term": term, "page_size": page_size},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["NCIThesaurus_search"]
