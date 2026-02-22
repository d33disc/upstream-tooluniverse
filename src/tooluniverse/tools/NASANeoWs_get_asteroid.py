"""
NASANeoWs_get_asteroid

Get detailed information about a specific near-Earth asteroid by its SPK-ID (Small-Body Perturber...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def NASANeoWs_get_asteroid(
    asteroid_id: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get detailed information about a specific near-Earth asteroid by its SPK-ID (Small-Body Perturber...

    Parameters
    ----------
    asteroid_id : str
        NASA SPK-ID of the asteroid. Examples: '3542519' (2010 PK9), '2021277' (21277...
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
        {"name": "NASANeoWs_get_asteroid", "arguments": {"asteroid_id": asteroid_id}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["NASANeoWs_get_asteroid"]
