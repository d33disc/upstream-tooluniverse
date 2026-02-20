"""
DictionaryAPI_lookup_word

Look up English word definitions, phonetics, synonyms, antonyms, and examples using the free Dict...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def DictionaryAPI_lookup_word(
    word: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Look up English word definitions, phonetics, synonyms, antonyms, and examples using the free Dict...

    Parameters
    ----------
    word : str
        English word to look up. Examples: 'hello', 'serendipity', 'ephemeral', 'ubiq...
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
        {"name": "DictionaryAPI_lookup_word", "arguments": {"word": word}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["DictionaryAPI_lookup_word"]
