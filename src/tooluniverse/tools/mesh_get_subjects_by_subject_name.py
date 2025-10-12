"""
mesh_get_subjects_by_subject_name

Find MeSH (Medical Subject Heading) subjects with matching names.
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


def mesh_get_subjects_by_subject_name(
    query: str,
    case_sensitive: Optional[bool] = False,
    exact_match: Optional[bool] = False,
    limit: Optional[int] = 50,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Find MeSH (Medical Subject Heading) subjects with matching names.

    Parameters
    ----------
    query : str
        Query string to search for in the name of each MeSH subject and the names of the subject's key concepts and concept synonyms.
    case_sensitive : bool
        Select True to perform a case-sensitive search for the query
    exact_match : bool
        Select True to require an exact match for the query
    limit : int
        Maximum number of results to return
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
            "name": "mesh_get_subjects_by_subject_name",
            "arguments": {
                "query": query,
                "case_sensitive": case_sensitive,
                "exact_match": exact_match,
                "limit": limit,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["mesh_get_subjects_by_subject_name"]
