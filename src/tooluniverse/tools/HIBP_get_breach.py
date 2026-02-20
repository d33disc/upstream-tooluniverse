"""
HIBP_get_breach

Get details of a specific data breach by its name from Have I Been Pwned. Returns complete breach...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def HIBP_get_breach(
    breach_name: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get details of a specific data breach by its name from Have I Been Pwned. Returns complete breach...

    Parameters
    ----------
    breach_name : str
        Breach name (case-insensitive). Examples: 'Adobe', 'LinkedIn', 'Yahoo', 'MyFi...
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
        {"name": "HIBP_get_breach", "arguments": {"breach_name": breach_name}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["HIBP_get_breach"]
