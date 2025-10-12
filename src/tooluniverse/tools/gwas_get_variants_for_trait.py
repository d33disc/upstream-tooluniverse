"""
gwas_get_variants_for_trait

Get all variants associated with a specific trait with pagination support.
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


def gwas_get_variants_for_trait(
    efo_trait: Optional[str] = None,
    size: Optional[int] = None,
    page: Optional[int] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Get all variants associated with a specific trait with pagination support.

    Parameters
    ----------
    efo_trait : str
        EFO trait identifier or name
    size : int
        Number of results to return per page
    page : int
        Page number for pagination
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
            "name": "gwas_get_variants_for_trait",
            "arguments": {"efo_trait": efo_trait, "size": size, "page": page},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["gwas_get_variants_for_trait"]
