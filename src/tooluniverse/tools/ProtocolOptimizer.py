"""
ProtocolOptimizer

Reviews an initial protocol and delivers targeted revisions that improve clarity, feasibility, risk-management, and evaluation rigor.
"""

from typing import Any, Optional, Callable
from tooluniverse import ToolUniverse

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = ToolUniverse()
        _client.load_tools()
    return _client


def ProtocolOptimizer(
    initial_protocol: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Reviews an initial protocol and delivers targeted revisions that improve clarity, feasibility, risk-management, and evaluation rigor.

    Parameters
    ----------
    initial_protocol : str

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
    return _get_client().run_one_function(
        {
            "name": "ProtocolOptimizer",
            "arguments": {"initial_protocol": initial_protocol},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ProtocolOptimizer"]
