"""
RESTCountries_get_by_code

Get detailed country information by ISO 3166-1 alpha-2 or alpha-3 code using the REST Countries A...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def RESTCountries_get_by_code(
    code: str,
    fields: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get detailed country information by ISO 3166-1 alpha-2 or alpha-3 code using the REST Countries A...

    Parameters
    ----------
    code : str
        ISO 3166-1 alpha-2 (e.g., 'US', 'DE', 'JP') or alpha-3 (e.g., 'USA', 'DEU', '...
    fields : str | Any
        Comma-separated list of fields to return. Examples: 'name,capital,population'...
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
            "name": "RESTCountries_get_by_code",
            "arguments": {"code": code, "fields": fields},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["RESTCountries_get_by_code"]
