"""
BindingDB_get_by_uniprot

Get protein-ligand binding affinity data from BindingDB by UniProt accession. Returns compounds w...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def BindingDB_get_by_uniprot(
    operation: str,
    uniprot_id: str,
    affinity_cutoff: Optional[int] = 10000,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Get protein-ligand binding affinity data from BindingDB by UniProt accession. Returns compounds w...

    Parameters
    ----------
    operation : str
        Operation type (fixed: get_by_uniprot)
    uniprot_id : str
        UniProt accession (e.g., P00533 for EGFR, P04637 for TP53)
    affinity_cutoff : int
        Maximum binding affinity in nM (default: 10000). Lower = more potent compound...
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
            "name": "BindingDB_get_by_uniprot",
            "arguments": {
                "operation": operation,
                "uniprot_id": uniprot_id,
                "affinity_cutoff": affinity_cutoff,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["BindingDB_get_by_uniprot"]
