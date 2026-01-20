"""
proteins_api_get_proteomics

Get proteomics data for a protein including mass spectrometry evidence, PTM sites, and expression...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def proteins_api_get_proteomics(
    accession: str,
    format: Optional[str] = "json",
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Get proteomics data for a protein including mass spectrometry evidence, PTM sites, and expression...

    Parameters
    ----------
    accession : str
        UniProt protein accession (e.g., 'P05067', 'P04637'). Use UniProt search or e...
    format : str
        Response format. JSON is recommended for most use cases.
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
    # Handle mutable defaults to avoid B006 linting error

    return get_shared_client().run_one_function(
        {
            "name": "proteins_api_get_proteomics",
            "arguments": {"accession": accession, "format": format},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["proteins_api_get_proteomics"]
