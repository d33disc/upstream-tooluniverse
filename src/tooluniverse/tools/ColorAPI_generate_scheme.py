"""
ColorAPI_generate_scheme

Generate a color scheme (palette) from a base color using The Color API. Returns harmonically rel...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def ColorAPI_generate_scheme(
    hex: str,
    mode: Optional[str | Any] = None,
    count: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Generate a color scheme (palette) from a base color using The Color API. Returns harmonically rel...

    Parameters
    ----------
    hex : str
        Base hex color code without '#'. Examples: 'ff5733', '4287f5', '2e86ab'
    mode : str | Any
        Color scheme type. Values: 'monochrome', 'monochrome-dark', 'monochrome-light...
    count : int | Any
        Number of colors in the scheme (default 5, max 10)
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
            "name": "ColorAPI_generate_scheme",
            "arguments": {"hex": hex, "mode": mode, "count": count},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ColorAPI_generate_scheme"]
