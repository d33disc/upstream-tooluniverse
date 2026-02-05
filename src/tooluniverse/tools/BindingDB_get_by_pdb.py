"""
BindingDB_get_by_pdb

Get binding affinity data for protein structures by PDB ID. Returns ligands with binding data for...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def BindingDB_get_by_pdb(
    operation: str,
    pdb_ids: str,
    affinity_cutoff: Optional[int] = 100,
    sequence_identity: Optional[int] = 90,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Get binding affinity data for protein structures by PDB ID. Returns ligands with binding data for...

    Parameters
    ----------
    operation : str
        Operation type (fixed: get_by_pdb)
    pdb_ids : str
        PDB ID(s), comma-separated (e.g., '1M17' or '1M17,3POZ')
    affinity_cutoff : int
        Maximum affinity in nM (default: 100)
    sequence_identity : int
        Minimum sequence identity % to PDB structure (default: 90)
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
            "name": "BindingDB_get_by_pdb",
            "arguments": {
                "operation": operation,
                "pdb_ids": pdb_ids,
                "affinity_cutoff": affinity_cutoff,
                "sequence_identity": sequence_identity,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["BindingDB_get_by_pdb"]
