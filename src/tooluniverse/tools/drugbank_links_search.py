"""
drugbank_links_search

Search the cross-reference table linking DrugBank IDs to external identifiers (CAS, KEGG, PubChem, ChEBI, PharmGKB, UniProt, etc.) and web resources.
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


def drugbank_links_search(
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
    Search the cross-reference table linking DrugBank IDs to external identifiers (CAS, KEGG, PubChem, ChEBI, PharmGKB, UniProt, etc.) and web resources.

    Parameters
    ----------
    query : str
        Free-text query (e.g. 'DB00002', 'Cetuximab').
    search_fields : list[Any]
        Columns to search. Choose from: 'DrugBank ID', 'Name', 'CAS Number', 'Drug Type', 'KEGG Compound ID', 'KEGG Drug ID', 'PubChem Compound ID', 'PubChem Substance ID', 'ChEBI ID', 'PharmGKB ID', 'HET ID', 'UniProt ID', 'Wikipedia ID', 'Drugs.com Link', 'NDC ID', 'ChemSpider ID', 'BindingDB ID', 'TTD ID'.
    case_sensitive : bool
        Match text with exact case if true.
    exact_match : bool
        Field value must equal query exactly if true; otherwise substring match.
    limit : int
        Maximum number of rows to return.
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
            "name": "drugbank_links_search",
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


__all__ = ["drugbank_links_search"]
