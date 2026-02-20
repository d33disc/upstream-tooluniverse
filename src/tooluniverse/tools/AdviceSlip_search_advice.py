"""
AdviceSlip_search_advice

Search for advice slips by keyword from the Advice Slip API (adviceslip.com). Returns all matchin...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def AdviceSlip_search_advice(
    query: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for advice slips by keyword from the Advice Slip API (adviceslip.com). Returns all matchin...

    Parameters
    ----------
    query : str
        Search query keyword (e.g., 'life', 'money', 'friends', 'work', 'happiness')
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
        {"name": "AdviceSlip_search_advice", "arguments": {"query": query}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["AdviceSlip_search_advice"]
