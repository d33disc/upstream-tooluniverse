"""
ColorAPI_identify_color

Identify a color by its hex code or RGB values using The Color API. Returns the color name, compl...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def ColorAPI_identify_color(
    hex: Optional[str | Any] = None,
    rgb: Optional[str | Any] = None,
    hsl: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Identify a color by its hex code or RGB values using The Color API. Returns the color name, compl...

    Parameters
    ----------
    hex : str | Any
        Hex color code without '#'. Examples: 'ff5733', '4287f5', '000000' (black), '...
    rgb : str | Any
        RGB color values as comma-separated string. Examples: '255,87,51', '66,135,24...
    hsl : str | Any
        HSL color values as comma-separated string. Examples: '14,100%,60%'
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
            "name": "ColorAPI_identify_color",
            "arguments": {"hex": hex, "rgb": rgb, "hsl": hsl},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ColorAPI_identify_color"]
