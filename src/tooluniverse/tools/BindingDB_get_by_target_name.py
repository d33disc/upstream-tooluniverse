"""
BindingDB_get_by_target_name

Search BindingDB by target protein name. Returns binding data for all ligands matching the target...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def BindingDB_get_by_target_name(
    operation: str,
    target_name: str,
    affinity_cutoff: Optional[int] = 1000,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Search BindingDB by target protein name. Returns binding data for all ligands matching the target...

    Parameters
    ----------
    operation : str
        Operation type (fixed: get_by_target_name)
    target_name : str
        Target protein name (e.g., 'EGFR', 'ABL kinase', 'COX-2')
    affinity_cutoff : int
        Maximum affinity in nM (default: 1000)
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
            "name": "BindingDB_get_by_target_name",
            "arguments": {
                "operation": operation,
                "target_name": target_name,
                "affinity_cutoff": affinity_cutoff,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["BindingDB_get_by_target_name"]
