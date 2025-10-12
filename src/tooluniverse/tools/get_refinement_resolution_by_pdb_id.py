"""
get_refinement_resolution_by_pdb_id

Retrieve the reported resolution from refinement data for X-ray structures.
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


def get_refinement_resolution_by_pdb_id(
    pdb_id: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve the reported resolution from refinement data for X-ray structures.

    Parameters
    ----------
    pdb_id : str
        PDB entry ID
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
            "name": "get_refinement_resolution_by_pdb_id",
            "arguments": {"pdb_id": pdb_id},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["get_refinement_resolution_by_pdb_id"]
