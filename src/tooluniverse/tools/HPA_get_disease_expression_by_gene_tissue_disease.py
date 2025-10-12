"""
HPA_get_disease_expression_by_gene_tissue_disease

Compare the expression level of a gene in specific disease state versus healthy state using gene name, tissue type, and disease name.
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


def HPA_get_disease_expression_by_gene_tissue_disease(
    gene_name: str,
    disease_name: str,
    tissue_type: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Compare the expression level of a gene in specific disease state versus healthy state using gene name, tissue type, and disease name.

    Parameters
    ----------
    gene_name : str
        Gene name or gene symbol, e.g., 'TP53', 'BRCA1', 'KRAS', etc.
    tissue_type : str
        Tissue type, e.g., 'brain', 'breast', 'colon', 'lung', etc., optional parameter.
    disease_name : str
        Disease name, supported diseases include: brain_cancer, breast_cancer, colon_cancer, lung_cancer, liver_cancer, prostate_cancer, kidney_cancer, pancreatic_cancer, stomach_cancer, ovarian_cancer.
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
            "name": "HPA_get_disease_expression_by_gene_tissue_disease",
            "arguments": {
                "gene_name": gene_name,
                "tissue_type": tissue_type,
                "disease_name": disease_name,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["HPA_get_disease_expression_by_gene_tissue_disease"]
