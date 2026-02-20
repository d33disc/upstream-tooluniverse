"""
CarbonIntensity_get_by_date

Get carbon intensity data for a specific date in the UK. Returns half-hourly actual and forecast ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def CarbonIntensity_get_by_date(
    date: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get carbon intensity data for a specific date in the UK. Returns half-hourly actual and forecast ...

    Parameters
    ----------
    date : str
        Date in YYYY-MM-DD format (e.g., '2024-01-15')
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
        {"name": "CarbonIntensity_get_by_date", "arguments": {"date": date}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["CarbonIntensity_get_by_date"]
