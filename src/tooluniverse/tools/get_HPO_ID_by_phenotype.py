"""
get_HPO_ID_by_phenotype

Retrieve the HPO ID of a phenotype or symptom.
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


def get_HPO_ID_by_phenotype(
    query: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve the HPO ID of a phenotype or symptom.

    Parameters
    ----------
    query : str
        One query phenotype or symptom.
    limit : int
        Number of entries to fetch.
    offset : int
        Number of initial entries to skip.
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
            "name": "get_HPO_ID_by_phenotype",
            "arguments": {"query": query, "limit": limit, "offset": offset},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["get_HPO_ID_by_phenotype"]
