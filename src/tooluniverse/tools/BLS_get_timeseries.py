"""
BLS_get_timeseries

Get economic time series data from the U.S. Bureau of Labor Statistics (BLS) public API. Returns ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def BLS_get_timeseries(
    seriesid: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get economic time series data from the U.S. Bureau of Labor Statistics (BLS) public API. Returns ...

    Parameters
    ----------
    seriesid : str
        BLS series ID(s). Examples: 'CUUR0000SA0' (CPI All Urban), 'LNS14000000' (Une...
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
        {"name": "BLS_get_timeseries", "arguments": {"seriesid": seriesid}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["BLS_get_timeseries"]
