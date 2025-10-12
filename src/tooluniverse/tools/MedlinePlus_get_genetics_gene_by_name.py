"""
MedlinePlus_get_genetics_gene_by_name

Get detailed information from MedlinePlus Genetics corresponding to gene name, supports JSON or XML format return.
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


def MedlinePlus_get_genetics_gene_by_name(
    gene: str,
    format: Optional[str] = "json",
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get detailed information from MedlinePlus Genetics corresponding to gene name, supports JSON or XML format return.

    Parameters
    ----------
    gene : str
        URL slug of gene name, e.g., "BRCA1", must match MedlinePlus page path.
    format : str
        Return format, options "json" or "xml", default "json".
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
            "name": "MedlinePlus_get_genetics_gene_by_name",
            "arguments": {"gene": gene, "format": format},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["MedlinePlus_get_genetics_gene_by_name"]
