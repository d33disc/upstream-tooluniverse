"""
GDC_get_mutation_frequency

Get mutation frequency statistics for a gene across TCGA projects
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def GDC_get_mutation_frequency(
    gene_symbol: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get mutation frequency statistics for a gene across TCGA projects

    Parameters
    ----------
    gene_symbol : str
        Gene symbol (e.g., 'TP53', 'KRAS')
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
        {
            "name": "GDC_get_mutation_frequency",
            "arguments": {"gene_symbol": gene_symbol},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["GDC_get_mutation_frequency"]
