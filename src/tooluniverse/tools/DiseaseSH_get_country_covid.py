"""
DiseaseSH_get_country_covid

Get COVID-19 statistics for a specific country using the Disease.sh API. Returns country-level ca...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def DiseaseSH_get_country_covid(
    country: str,
    yesterday: Optional[bool | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get COVID-19 statistics for a specific country using the Disease.sh API. Returns country-level ca...

    Parameters
    ----------
    country : str
        Country name or ISO 3166-1 alpha-2/alpha-3 code. Examples: 'USA', 'India', 'B...
    yesterday : bool | Any
        If true, returns yesterday's data. Default: false
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
            "name": "DiseaseSH_get_country_covid",
            "arguments": {"country": country, "yesterday": yesterday},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["DiseaseSH_get_country_covid"]
