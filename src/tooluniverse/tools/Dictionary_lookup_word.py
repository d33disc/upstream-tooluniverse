"""
Dictionary_lookup_word

Look up the definition, pronunciation, and usage of an English word using the Free Dictionary API...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Dictionary_lookup_word(
    word: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Look up the definition, pronunciation, and usage of an English word using the Free Dictionary API...

    Parameters
    ----------
    word : str
        English word to look up. Examples: 'serendipity', 'algorithm', 'photosynthesi...
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
        {"name": "Dictionary_lookup_word", "arguments": {"word": word}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Dictionary_lookup_word"]
