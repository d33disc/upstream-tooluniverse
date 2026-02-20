"""
UrbanDictionary_define

Look up slang terms, informal expressions, and internet jargon on Urban Dictionary. Returns crowd...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def UrbanDictionary_define(
    term: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Look up slang terms, informal expressions, and internet jargon on Urban Dictionary. Returns crowd...

    Parameters
    ----------
    term : str
        Slang term or phrase to define (e.g., 'YOLO', 'slay', 'sigma', 'rizz', 'gasli...
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
        {"name": "UrbanDictionary_define", "arguments": {"term": term}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["UrbanDictionary_define"]
