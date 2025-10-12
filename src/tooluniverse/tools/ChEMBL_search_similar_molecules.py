"""
ChEMBL_search_similar_molecules

Search for molecules similar to a given SMILES, chembl_id, or compound or drug name, using the ChEMBL Web Services.
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


def ChEMBL_search_similar_molecules(
    query: str,
    similarity_threshold: Optional[int] = 80,
    max_results: Optional[int] = 20,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for molecules similar to a given SMILES, chembl_id, or compound or drug name, using the ChEMBL Web Services.

    Parameters
    ----------
    query : str
        SMILES string, chembl_id, or compound or drug name.
    similarity_threshold : int
        Similarity threshold (0–100).
    max_results : int
        Maximum number of results to return.
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
            "name": "ChEMBL_search_similar_molecules",
            "arguments": {
                "query": query,
                "similarity_threshold": similarity_threshold,
                "max_results": max_results,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ChEMBL_search_similar_molecules"]
