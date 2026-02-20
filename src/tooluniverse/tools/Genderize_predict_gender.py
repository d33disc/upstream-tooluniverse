"""
Genderize_predict_gender

Predict the likely gender of a person based on their first name using the Genderize.io API. Retur...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Genderize_predict_gender(
    name: str,
    country_id: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Predict the likely gender of a person based on their first name using the Genderize.io API. Retur...

    Parameters
    ----------
    name : str
        First name to analyze. Examples: 'James', 'Emma', 'Alex', 'Jordan', 'Taylor'
    country_id : str | Any
        ISO 3166-1 alpha-2 country code for country-specific prediction. Examples: 'U...
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
            "name": "Genderize_predict_gender",
            "arguments": {"name": name, "country_id": country_id},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Genderize_predict_gender"]
