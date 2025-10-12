"""
get_protein_metadata_by_pdb_id

Retrieve basic protein structure metadata, including structure title, experimental method, resolution, and initial release date.
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


def get_protein_metadata_by_pdb_id(
    pdb_id: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Retrieve basic protein structure metadata, including structure title, experimental method, resolution, and initial release date.

    Parameters
    ----------
    pdb_id : str
        4-character RCSB PDB ID of the protein
    stream_callback : Callable, optional
        Callback for streaming output
    use_cache : bool, default False
        Enable caching
    validate : bool, default True
        Validate parameters

    Returns
    -------
    dict[str, Any]
    """
    return _get_client().run_one_function(
        {"name": "get_protein_metadata_by_pdb_id", "arguments": {"pdb_id": pdb_id}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["get_protein_metadata_by_pdb_id"]
