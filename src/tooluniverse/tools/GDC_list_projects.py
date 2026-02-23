"""
GDC_list_projects

List GDC projects (TCGA, TARGET, etc.) with summary statistics
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def GDC_list_projects(
    program: Optional[str] = None,
    size: Optional[int] = 20,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    List GDC projects (TCGA, TARGET, etc.) with summary statistics

    Parameters
    ----------
    program : str
        Filter by program (e.g., 'TCGA', 'TARGET')
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
        {"name": "GDC_list_projects", "arguments": {"program": program, "size": size}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["GDC_list_projects"]
