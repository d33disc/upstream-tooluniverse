"""
get_binding_affinity_by_pdb_id

Retrieve binding affinity constants (Kd, Ki, IC50) associated with ligands in a PDB entry.
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


def get_binding_affinity_by_pdb_id(
    pdb_id: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve binding affinity constants (Kd, Ki, IC50) associated with ligands in a PDB entry.

    Parameters
    ----------
    pdb_id : str
        RCSB PDB ID (e.g., 1A8M)
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
        {"name": "get_binding_affinity_by_pdb_id", "arguments": {"pdb_id": pdb_id}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["get_binding_affinity_by_pdb_id"]
