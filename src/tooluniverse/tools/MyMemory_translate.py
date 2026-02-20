"""
MyMemory_translate

Translate text between languages using MyMemory, the world's largest collaborative translation me...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def MyMemory_translate(
    q: str,
    langpair: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Translate text between languages using MyMemory, the world's largest collaborative translation me...

    Parameters
    ----------
    q : str
        Text to translate (max 500 characters per request). Examples: 'Hello, how are...
    langpair : str
        Language pair in format 'source|target' using ISO 639-1 codes. Examples: 'en|...
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
        {"name": "MyMemory_translate", "arguments": {"q": q, "langpair": langpair}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["MyMemory_translate"]
