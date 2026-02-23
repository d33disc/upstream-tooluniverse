"""
GDC_list_files

List NCI GDC files via /files with optional data_type filter
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def GDC_list_files(
    data_type: Optional[str] = None,
    size: Optional[int] = 10,
    offset: Optional[int] = 0,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    List NCI GDC files via /files with optional data_type filter

    Parameters
    ----------
    data_type : str
        Data type filter (e.g., 'Gene Expression Quantification')
    size : int
        Number of results (1–100)
    offset : int
        Offset for pagination (0-based)
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
            "name": "GDC_list_files",
            "arguments": {"data_type": data_type, "size": size, "offset": offset},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["GDC_list_files"]
