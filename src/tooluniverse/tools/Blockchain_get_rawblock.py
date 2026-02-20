"""
Blockchain_get_rawblock

Get detailed Bitcoin block data by block hash from the Blockchain.info API. Returns block header ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Blockchain_get_rawblock(
    block_hash: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get detailed Bitcoin block data by block hash from the Blockchain.info API. Returns block header ...

    Parameters
    ----------
    block_hash : str
        Bitcoin block hash (64-character hex string). Example: '000000000019d6689c085...
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
        {"name": "Blockchain_get_rawblock", "arguments": {"block_hash": block_hash}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Blockchain_get_rawblock"]
