"""
gwas_get_associations_for_snp

Get all associations for a specific SNP with optional sorting.
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


def gwas_get_associations_for_snp(
    rs_id: Optional[str] = None,
    sort: Optional[str] = None,
    direction: Optional[str] = None,
    size: Optional[int] = None,
    page: Optional[int] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Get all associations for a specific SNP with optional sorting.

    Parameters
    ----------
    rs_id : str
        dbSNP rs identifier
    sort : str
        Sort field (e.g., 'p_value', 'or_value')
    direction : str
        Sort direction ('asc' or 'desc')
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
            "name": "gwas_get_associations_for_snp",
            "arguments": {
                "rs_id": rs_id,
                "sort": sort,
                "direction": direction,
                "size": size,
                "page": page,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["gwas_get_associations_for_snp"]
