"""
Blockchain_get_address

Get Bitcoin address balance and recent transactions from the Blockchain.info API. Returns total r...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Blockchain_get_address(
    address: str,
    limit: Optional[int | Any] = None,
    offset: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get Bitcoin address balance and recent transactions from the Blockchain.info API. Returns total r...

    Parameters
    ----------
    address : str
        Bitcoin address (legacy, SegWit, or Bech32 format). Example: '1A1zP1eP5QGefi2...
    limit : int | Any
        Maximum number of transactions to return (default 50, max 100)
    offset : int | Any
        Transaction offset for pagination
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
            "name": "Blockchain_get_address",
            "arguments": {"address": address, "limit": limit, "offset": offset},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Blockchain_get_address"]
