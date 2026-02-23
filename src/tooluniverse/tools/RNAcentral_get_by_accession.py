"""
RNAcentral_get_by_accession

Get RNAcentral entry by accession
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def RNAcentral_get_by_accession(
    accession: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get RNAcentral entry by accession

    Parameters
    ----------
    accession : str
        RNAcentral accession
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
    # Handle mutable defaults to avoid B006 linting error

    return get_shared_client().run_one_function(
        {"name": "RNAcentral_get_by_accession", "arguments": {"accession": accession}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["RNAcentral_get_by_accession"]
