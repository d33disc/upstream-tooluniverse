"""
embedding_database_search

Search for semantically similar documents in an embedding database. Uses OpenAI embeddings to convert query text to vectors and performs similarity search using FAISS with optional metadata filtering.
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


def embedding_database_search(
    database_name: str,
    query: str,
    action: Optional[str] = None,
    top_k: Optional[int] = 5,
    filters: Optional[dict[str, Any]] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for semantically similar documents in an embedding database. Uses OpenAI embeddings to convert query text to vectors and performs similarity search using FAISS with optional metadata filtering.

    Parameters
    ----------
    action : str
        Action to search the database
    database_name : str
        Name of the database to search in
    query : str
        Query text to find similar documents for
    top_k : int
        Number of most similar documents to return
    filters : dict[str, Any]
        Optional metadata filters to apply to search results
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
    if filters is None:
        filters = {}

    return _get_client().run_one_function(
        {
            "name": "embedding_database_search",
            "arguments": {
                "action": action,
                "database_name": database_name,
                "query": query,
                "top_k": top_k,
                "filters": filters,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["embedding_database_search"]
