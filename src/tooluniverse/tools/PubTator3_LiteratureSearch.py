"""
PubTator3_LiteratureSearch

Find PubMed articles that match a keyword, a PubTator entity ID (e.g. “@GENE_BRAF”), or an entity-to-entity relation expression (e.g. “relations:treat|@CHEMICAL_Doxorubicin|@DISEASE_Neoplasms”).
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


def PubTator3_LiteratureSearch(
    query: str,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Find PubMed articles that match a keyword, a PubTator entity ID (e.g. “@GENE_BRAF”), or an entity-to-entity relation expression (e.g. “relations:treat|@CHEMICAL_Doxorubicin|@DISEASE_Neoplasms”).

    Parameters
    ----------
    query : str
        What you want to search for. This can be plain keywords, a single PubTator ID, or the special relation syntax shown above.
    page : int
        Zero-based results page (optional; default = 0).
    page_size : int
        How many PMIDs to return per page (optional; default = 20, maximum = 200).
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
            "name": "PubTator3_LiteratureSearch",
            "arguments": {"query": query, "page": page, "page_size": page_size},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["PubTator3_LiteratureSearch"]
