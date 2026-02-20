"""
AdviceSlip_get_random_advice

Get a random piece of advice from the Advice Slip API (adviceslip.com). Returns a slip containing...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def AdviceSlip_get_random_advice(
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get a random piece of advice from the Advice Slip API (adviceslip.com). Returns a slip containing...

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
        {"name": "AdviceSlip_get_random_advice", "arguments": {}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["AdviceSlip_get_random_advice"]
