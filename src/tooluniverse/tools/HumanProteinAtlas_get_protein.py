"""
HumanProteinAtlas_get_protein

Get comprehensive protein data for a gene from the Human Protein Atlas (HPA) by Ensembl gene ID. ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def HumanProteinAtlas_get_protein(
    ensembl_id: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get comprehensive protein data for a gene from the Human Protein Atlas (HPA) by Ensembl gene ID. ...

    Parameters
    ----------
    ensembl_id : str
        Ensembl gene ID (e.g., 'ENSG00000141510' for TP53, 'ENSG00000012048' for BRCA...
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
            "name": "HumanProteinAtlas_get_protein",
            "arguments": {"ensembl_id": ensembl_id},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["HumanProteinAtlas_get_protein"]
