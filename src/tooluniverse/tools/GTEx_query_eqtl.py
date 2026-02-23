"""
GTEx_query_eqtl

Query GTEx single-tissue eQTL via /association/singleTissueEqtl
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def GTEx_query_eqtl(
    ensembl_gene_id: str,
    page: Optional[int] = 1,
    size: Optional[int] = 10,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Query GTEx single-tissue eQTL via /association/singleTissueEqtl

    Parameters
    ----------
    ensembl_gene_id : str
        Ensembl gene ID, e.g., ENSG00000141510
    page : int
        Page number (1-based)
    size : int
        Page size (1–100)
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
            "name": "GTEx_query_eqtl",
            "arguments": {
                "ensembl_gene_id": ensembl_gene_id,
                "page": page,
                "size": size,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["GTEx_query_eqtl"]
