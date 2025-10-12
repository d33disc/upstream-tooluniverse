"""
PubChem_search_compounds_by_similarity

Search by similarity (Tanimoto coefficient), returns CID list of compounds with similarity above threshold to given SMILES molecule, returns no more than 10 CIDs (MaxRecords=10)
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


def PubChem_search_compounds_by_similarity(
    smiles: str,
    threshold: Optional[float] = 0.9,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search by similarity (Tanimoto coefficient), returns CID list of compounds with similarity above threshold to given SMILES molecule, returns no more than 10 CIDs (MaxRecords=10)

    Parameters
    ----------
    smiles : str
        SMILES expression of target molecule.
    threshold : float
        Similarity threshold (between 0 and 1), e.g., 0.9 means 90% similarity.
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
            "name": "PubChem_search_compounds_by_similarity",
            "arguments": {"smiles": smiles, "threshold": threshold},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["PubChem_search_compounds_by_similarity"]
