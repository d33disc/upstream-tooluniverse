"""
RESTCountries_get_by_language

Find all countries where a specific language is spoken using the REST Countries API. Returns coun...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def RESTCountries_get_by_language(
    language: str,
    fields: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Find all countries where a specific language is spoken using the REST Countries API. Returns coun...

    Parameters
    ----------
    language : str
        Language name (e.g., 'french', 'spanish', 'arabic', 'chinese') or ISO 639-1/6...
    fields : str | Any
        Comma-separated fields to return. Examples: 'name,languages,population', 'nam...
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
            "name": "RESTCountries_get_by_language",
            "arguments": {"language": language, "fields": fields},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["RESTCountries_get_by_language"]
