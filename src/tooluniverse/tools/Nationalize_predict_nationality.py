"""
Nationalize_predict_nationality

Predict the likely nationality/country origin of a person based on their first name using the Nat...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Nationalize_predict_nationality(
    name: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Predict the likely nationality/country origin of a person based on their first name using the Nat...

    Parameters
    ----------
    name : str
        First name to analyze for nationality. Examples: 'Kim', 'Mohammed', 'Maria', ...
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
        {"name": "Nationalize_predict_nationality", "arguments": {"name": name}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Nationalize_predict_nationality"]
