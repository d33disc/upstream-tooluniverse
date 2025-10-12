"""
get_protein_classification_by_pdb_id

Get the classification of the protein structure (e.g., transferase, oxidoreductase).
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


def get_protein_classification_by_pdb_id(
    pdb_id: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get the classification of the protein structure (e.g., transferase, oxidoreductase).

    Parameters
    ----------
    pdb_id : str
        PDB ID of the entry
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
            "name": "get_protein_classification_by_pdb_id",
            "arguments": {"pdb_id": pdb_id},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["get_protein_classification_by_pdb_id"]
