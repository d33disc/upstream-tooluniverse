"""
drugbank_full_search

Search the cleaned DrugBank dataframe (one row per drug) by ID, common name, or synonym. Returns identifiers, ATC, main pharmacology text fields, and protein partners. For best results, it is recommended that one uses `drugbank_vocab_search` to obtain DrugBank ID from other keywords first, and use this tool with DrugBank ID.
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


def drugbank_full_search(
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
    Search the cleaned DrugBank dataframe (one row per drug) by ID, common name, or synonym. Returns identifiers, ATC, main pharmacology text fields, and protein partners. For best results, it is recommended that one uses `drugbank_vocab_search` to obtain DrugBank ID from other keywords first, and use this tool with DrugBank ID.

    Parameters
    ----------
    query : str
        Free-text query (e.g. 'DB00945', 'acetylsalicylic', 'Acarbosa').
    search_fields : list[Any]
        Columns to search in. Choose from: 'drugbank_id', 'name', 'synonyms'.
    case_sensitive : bool
        Match text with exact case if true.
    exact_match : bool
        Field value must equal query exactly if true; otherwise substring match.
    limit : int
        Max number of rows to return.
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
            "name": "drugbank_full_search",
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


__all__ = ["drugbank_full_search"]
