"""
GDC_get_ssm_by_gene

Get somatic mutations (SSMs) for a gene across TCGA/GDC projects
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def GDC_get_ssm_by_gene(
    gene_symbol: str,
    project_id: Optional[str] = None,
    size: Optional[int] = 20,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get somatic mutations (SSMs) for a gene across TCGA/GDC projects

    Parameters
    ----------
    gene_symbol : str
        Gene symbol (e.g., 'TP53', 'EGFR', 'BRAF')
    project_id : str
        Optional: Filter by project (e.g., 'TCGA-BRCA')
    size : int
        Number of results (1–100)
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
            "name": "GDC_get_ssm_by_gene",
            "arguments": {
                "gene_symbol": gene_symbol,
                "project_id": project_id,
                "size": size,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["GDC_get_ssm_by_gene"]
