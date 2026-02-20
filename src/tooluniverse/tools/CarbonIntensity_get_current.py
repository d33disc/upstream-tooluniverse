"""
CarbonIntensity_get_current

Get the current carbon intensity of electricity generation for the UK national grid. Returns actu...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def CarbonIntensity_get_current(
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get the current carbon intensity of electricity generation for the UK national grid. Returns actu...

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
        {"name": "CarbonIntensity_get_current", "arguments": {}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["CarbonIntensity_get_current"]
