"""
FDA_get_drug_generic_name

Get the drug’s generic name based on the drug's generic or brand name.
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


def FDA_get_drug_generic_name(
    drug_name: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get the drug’s generic name based on the drug's generic or brand name.

    Parameters
    ----------
    drug_name : str
        The generic or brand name of the drug.
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
        {"name": "FDA_get_drug_generic_name", "arguments": {"drug_name": drug_name}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["FDA_get_drug_generic_name"]
