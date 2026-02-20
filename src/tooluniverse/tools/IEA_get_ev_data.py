"""
IEA_get_ev_data

Get electric vehicle (EV) statistics from the International Energy Agency (IEA) Global EV Data Ex...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def IEA_get_ev_data(
    category: Optional[str | Any] = None,
    parameter: Optional[str | Any] = None,
    mode: Optional[str | Any] = None,
    zone: Optional[str | Any] = None,
    year: Optional[int | Any] = None,
    unit: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get electric vehicle (EV) statistics from the International Energy Agency (IEA) Global EV Data Ex...

    Parameters
    ----------
    category : str | Any
        Data category. Values: 'Historical' (default), 'Projection (STEPS)', 'Project...
    parameter : str | Any
        Data parameter. Values: 'EV sales', 'EV sales share', 'EV stock', 'EV stock s...
    mode : str | Any
        Vehicle mode. Values: 'Cars', 'Vans', 'Trucks', 'Buses', 'Two/three-wheelers'...
    zone : str | Any
        Geographic zone/region. Examples: 'World', 'China', 'Europe', 'USA', 'India',...
    year : int | Any
        Year of data. Examples: 2020, 2021, 2022, 2023. Leave null for all years.
    unit : str | Any
        Unit. Examples: 'Vehicles', 'percent', 'Thousand'. Default: depends on parameter
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
            "name": "IEA_get_ev_data",
            "arguments": {
                "category": category,
                "parameter": parameter,
                "mode": mode,
                "zone": zone,
                "year": year,
                "unit": unit,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["IEA_get_ev_data"]
