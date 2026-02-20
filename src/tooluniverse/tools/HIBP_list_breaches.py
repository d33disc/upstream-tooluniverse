"""
HIBP_list_breaches

Get the complete list of all public data breaches tracked by Have I Been Pwned (HIBP). Returns al...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def HIBP_list_breaches(
    domain: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get the complete list of all public data breaches tracked by Have I Been Pwned (HIBP). Returns al...

    Parameters
    ----------
    domain : str | Any
        Filter breaches by domain name. Example: 'adobe.com', 'linkedin.com', 'yahoo....
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
        {"name": "HIBP_list_breaches", "arguments": {"domain": domain}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["HIBP_list_breaches"]
