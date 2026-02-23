"""
ENCODE_search_experiments

Search ENCODE experiments
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def ENCODE_search_experiments(
    assay_title: Optional[str] = None,
    target: Optional[str] = None,
    organism: Optional[str] = None,
    status: Optional[str] = "released",
    limit: Optional[int] = 10,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search ENCODE experiments

    Parameters
    ----------
    assay_title : str

    target : str

    organism : str

    status : str

    limit : int

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
            "name": "ENCODE_search_experiments",
            "arguments": {
                "assay_title": assay_title,
                "target": target,
                "organism": organism,
                "status": status,
                "limit": limit,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ENCODE_search_experiments"]
