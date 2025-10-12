"""
HPA_get_cancer_prognostics_by_gene

Retrieve prognostic value of a gene across various cancer types, indicating if its expression level correlates with patient survival outcomes.
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


def HPA_get_cancer_prognostics_by_gene(
    ensembl_id: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve prognostic value of a gene across various cancer types, indicating if its expression level correlates with patient survival outcomes.

    Parameters
    ----------
    ensembl_id : str
        Ensembl Gene ID of the gene to check, e.g., 'ENSG00000141510' for TP53, 'ENSG00000012048' for BRCA1.
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
            "name": "HPA_get_cancer_prognostics_by_gene",
            "arguments": {"ensembl_id": ensembl_id},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["HPA_get_cancer_prognostics_by_gene"]
