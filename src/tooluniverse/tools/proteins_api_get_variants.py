"""
proteins_api_get_variants

Get variation data for a protein including ClinVar, COSMIC, and other variant annotations. Note: ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def proteins_api_get_variants(
    accession: str,
    format: Optional[str] = "json",
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Get variation data for a protein including ClinVar, COSMIC, and other variant annotations. Note: ...

    Parameters
    ----------
    accession : str
        UniProt protein accession
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
            "name": "proteins_api_get_variants",
            "arguments": {"accession": accession, "format": format},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["proteins_api_get_variants"]
