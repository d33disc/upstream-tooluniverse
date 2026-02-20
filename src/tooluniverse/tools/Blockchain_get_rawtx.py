"""
Blockchain_get_rawtx

Get detailed Bitcoin transaction data by transaction hash from the Blockchain.info API. Returns i...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Blockchain_get_rawtx(
    tx_hash: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get detailed Bitcoin transaction data by transaction hash from the Blockchain.info API. Returns i...

    Parameters
    ----------
    tx_hash : str
        Bitcoin transaction hash (64-character hex string, also known as txid)
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
        {"name": "Blockchain_get_rawtx", "arguments": {"tx_hash": tx_hash}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Blockchain_get_rawtx"]
