"""
drugbank_vocab_search

Search the DrugBank vocabulary dataset for drugs by name, ID, synonyms, or other fields using text-based queries. Returns detailed drug information including DrugBank ID, common name, CAS number, UNII, and synonyms.
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


def drugbank_vocab_search(
    query: Optional[str] = None,
    search_fields: Optional[list[Any]] = None,
    case_sensitive: Optional[bool] = None,
    exact_match: Optional[bool] = None,
    limit: Optional[int] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Search the DrugBank vocabulary dataset for drugs by name, ID, synonyms, or other fields using text-based queries. Returns detailed drug information including DrugBank ID, common name, CAS number, UNII, and synonyms.

    Parameters
    ----------
    query : str
        Search query string. Can be drug name, synonym, DrugBank ID, or any text to search for.
    search_fields : list[Any]
        Fields to search in. Available fields: 'DrugBank ID', 'Accession Numbers', 'Common name', 'CAS', 'UNII', 'Synonyms', 'Standard InChI Key'.
    case_sensitive : bool
        Whether the search should be case sensitive.
    exact_match : bool
        Whether to perform exact matching instead of substring matching.
    limit : int
        Maximum number of results to return.
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
        {
            "name": "drugbank_vocab_search",
            "arguments": {
                "query": query,
                "search_fields": search_fields,
                "case_sensitive": case_sensitive,
                "exact_match": exact_match,
                "limit": limit,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["drugbank_vocab_search"]
