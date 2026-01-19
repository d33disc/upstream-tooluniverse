"""
proteins_api_get_protein

Get comprehensive protein information from Proteins API by UniProt accession. Returns protein ann...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def proteins_api_get_protein(
    accession: str,
    format: Optional[str] = "json",
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Get comprehensive protein information from Proteins API by UniProt accession. Returns protein ann...

    Parameters
    ----------
    accession : str
        UniProt protein accession (e.g., 'P05067', 'P04637')
    format : str

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
            "name": "proteins_api_get_protein",
            "arguments": {"accession": accession, "format": format},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["proteins_api_get_protein"]
