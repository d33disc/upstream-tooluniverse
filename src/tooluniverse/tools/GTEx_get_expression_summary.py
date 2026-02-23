"""
GTEx_get_expression_summary

Get GTEx expression summary for a gene via /expression/geneExpression
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def GTEx_get_expression_summary(
    ensembl_gene_id: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get GTEx expression summary for a gene via /expression/geneExpression

    Parameters
    ----------
    ensembl_gene_id : str
        Ensembl gene ID, e.g., ENSG00000141510
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
            "name": "GTEx_get_expression_summary",
            "arguments": {"ensembl_gene_id": ensembl_gene_id},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["GTEx_get_expression_summary"]
