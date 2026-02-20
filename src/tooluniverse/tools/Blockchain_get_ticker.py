"""
Blockchain_get_ticker

Get current Bitcoin exchange rates in 20+ fiat currencies from Blockchain.info. Returns 15-minute...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Blockchain_get_ticker(
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get current Bitcoin exchange rates in 20+ fiat currencies from Blockchain.info. Returns 15-minute...

    Parameters
    ----------
    No parameters
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
        {"name": "Blockchain_get_ticker", "arguments": {}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Blockchain_get_ticker"]
