"""
BibleAPI_get_verse

Get Bible verse text by reference using the Bible-API.com service. Returns the verse text, refere...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def BibleAPI_get_verse(
    reference: str,
    translation: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get Bible verse text by reference using the Bible-API.com service. Returns the verse text, refere...

    Parameters
    ----------
    reference : str
        Bible verse reference. Examples: 'john 3:16', 'genesis 1:1', 'psalms 23', 'ma...
    translation : str | Any
        Bible translation. Values: 'web' (World English Bible, default), 'kjv', 'asv'...
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
        {
            "name": "BibleAPI_get_verse",
            "arguments": {"reference": reference, "translation": translation},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["BibleAPI_get_verse"]
