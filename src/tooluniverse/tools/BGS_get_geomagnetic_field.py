"""
BGS_get_geomagnetic_field

Get Earth's geomagnetic field values at any location using the International Geomagnetic Referenc...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def BGS_get_geomagnetic_field(
    latitude: float,
    longitude: float,
    date: str,
    altitude: Optional[float | Any] = None,
    model: Optional[str | Any] = None,
    model_revision: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get Earth's geomagnetic field values at any location using the International Geomagnetic Referenc...

    Parameters
    ----------
    latitude : float
        Geographic latitude in decimal degrees (positive = north, -90 to 90). Example...
    longitude : float
        Geographic longitude in decimal degrees (positive = east, -180 to 180). Examp...
    date : str
        Date for field computation in YYYY-MM-DD format (IGRF valid 1900-2025). Examp...
    altitude : float | Any
        Altitude above sea level in km (default 0). Examples: 0 (sea level), 10 (airc...
    model : str | Any
        Geomagnetic model to use: 'igrf' (IGRF-13, 1900-2025, default) or 'wmm' (Worl...
    model_revision : str | Any
        Model revision: '13' for IGRF-13 (default), '2020' for WMM-2020
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
            "name": "BGS_get_geomagnetic_field",
            "arguments": {
                "latitude": latitude,
                "longitude": longitude,
                "date": date,
                "altitude": altitude,
                "model": model,
                "model_revision": model_revision,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["BGS_get_geomagnetic_field"]
