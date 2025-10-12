"""
PubChem_get_associated_patents_by_CID

Get a list of patents associated with a specific compound CID.
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


def PubChem_get_associated_patents_by_CID(
    cid: int,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get a list of patents associated with a specific compound CID.

    Parameters
    ----------
    cid : int
        PubChem compound ID to query, e.g., 2244 (Aspirin).
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
        {"name": "PubChem_get_associated_patents_by_CID", "arguments": {"cid": cid}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["PubChem_get_associated_patents_by_CID"]
