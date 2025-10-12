"""
get_assembly_summary

Get key assembly composition and symmetry summary for an assembly associated with a PDB entry.
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


def get_assembly_summary(
    assembly_id: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get key assembly composition and symmetry summary for an assembly associated with a PDB entry.

    Parameters
    ----------
    assembly_id : str
        Assembly ID in format 'PDBID-assemblyNumber' (e.g., '1A8M-1')
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
        {"name": "get_assembly_summary", "arguments": {"assembly_id": assembly_id}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["get_assembly_summary"]
