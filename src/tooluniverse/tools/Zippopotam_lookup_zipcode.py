"""
Zippopotam_lookup_zipcode

Look up geographic information for a postal/ZIP code using the Zippopotam.us API. Returns city na...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Zippopotam_lookup_zipcode(
    country: str,
    zipcode: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Look up geographic information for a postal/ZIP code using the Zippopotam.us API. Returns city na...

    Parameters
    ----------
    country : str
        Two-letter ISO country code. Examples: 'us' (United States), 'gb' (UK), 'de' ...
    zipcode : str
        Postal/ZIP code to look up. Examples: '90210' (Beverly Hills CA), 'SW1A 1AA' ...
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
            "name": "Zippopotam_lookup_zipcode",
            "arguments": {"country": country, "zipcode": zipcode},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Zippopotam_lookup_zipcode"]
