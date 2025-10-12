"""
Wikidata_SPARQL_query

Execute SPARQL queries against Wikidata to retrieve structured data. This tool powers Scholia-style visualizations and can query academic topics, authors, institutions, and research relationships.
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


def Wikidata_SPARQL_query(
    sparql: str,
    max_results: Optional[int] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> list[Any]:
    """
    Execute SPARQL queries against Wikidata to retrieve structured data. This tool powers Scholia-style visualizations and can query academic topics, authors, institutions, and research relationships.

    Parameters
    ----------
    sparql : str
        SPARQL query string to execute against Wikidata. Use SPARQL syntax to query academic entities, relationships, and properties.
    max_results : int
        Optional result limit override. If not specified, uses the LIMIT clause in the SPARQL query or returns all results.
    stream_callback : Callable, optional
        Callback for streaming output
    use_cache : bool, default False
        Enable caching
    validate : bool, default True
        Validate parameters

    Returns
    -------
    list[Any]
    """
    return _get_client().run_one_function(
        {
            "name": "Wikidata_SPARQL_query",
            "arguments": {"sparql": sparql, "max_results": max_results},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Wikidata_SPARQL_query"]
