"""
cellosaurus_query_converter

Convert natural language queries to Solr syntax for Cellosaurus API searches. Uses semantic similarity to map terms to appropriate fields.
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


def cellosaurus_query_converter(
    query: str,
    include_explanation: Optional[bool] = True,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Convert natural language queries to Solr syntax for Cellosaurus API searches. Uses semantic similarity to map terms to appropriate fields.

    Parameters
    ----------
    query : str
        Natural language query to convert to Solr syntax (e.g., 'human cancer cells', 'HeLa cells from lung tissue')
    include_explanation : bool
        Whether to include detailed explanation of the conversion process
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
            "name": "cellosaurus_query_converter",
            "arguments": {"query": query, "include_explanation": include_explanation},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["cellosaurus_query_converter"]
