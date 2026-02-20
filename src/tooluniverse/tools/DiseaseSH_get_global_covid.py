"""
DiseaseSH_get_global_covid

Get global COVID-19 statistics using the Disease.sh API. Returns total worldwide cases, deaths, r...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def DiseaseSH_get_global_covid(
    yesterday: Optional[bool | Any] = None,
    allowNull: Optional[bool | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get global COVID-19 statistics using the Disease.sh API. Returns total worldwide cases, deaths, r...

    Parameters
    ----------
    yesterday : bool | Any
        If true, returns yesterday's data instead of today's. Default: false
    allowNull : bool | Any
        If true, allows null values in response. Default: false
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
            "name": "DiseaseSH_get_global_covid",
            "arguments": {"yesterday": yesterday, "allowNull": allowNull},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["DiseaseSH_get_global_covid"]
