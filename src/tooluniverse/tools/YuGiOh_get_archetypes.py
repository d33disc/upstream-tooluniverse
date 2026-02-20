"""
YuGiOh_get_archetypes

List all Yu-Gi-Oh! card archetypes from the YGOPRODeck API. Archetypes are groups of related card...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def YuGiOh_get_archetypes(
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    List all Yu-Gi-Oh! card archetypes from the YGOPRODeck API. Archetypes are groups of related card...

    Parameters
    ----------
    No parameters
    stream_callback : Callable, optional
        Callback for streaming output
    use_cache : bool, default False
        Enable caching
    validate : bool, default True
        Validate parameters

    Returns
    -------
    Any
    """
    # Handle mutable defaults to avoid B006 linting error

    return get_shared_client().run_one_function(
        {"name": "YuGiOh_get_archetypes", "arguments": {}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["YuGiOh_get_archetypes"]
