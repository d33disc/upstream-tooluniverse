"""
PubChem_search_compounds_by_substructure

Search for all CIDs in PubChem that contain the given substructure (SMILES).
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


def PubChem_search_compounds_by_substructure(
    smiles: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for all CIDs in PubChem that contain the given substructure (SMILES).

    Parameters
    ----------
    smiles : str
        SMILES of substructure (e.g., "c1ccccc1" corresponds to benzene ring).
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
            "name": "PubChem_search_compounds_by_substructure",
            "arguments": {"smiles": smiles},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["PubChem_search_compounds_by_substructure"]
