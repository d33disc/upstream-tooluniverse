"""
Smithsonian_search_collection

Search the Smithsonian Institution's open access collection of 5M+ digitized artifacts, specimens...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Smithsonian_search_collection(
    q: str,
    unit_code: Optional[str | Any] = None,
    type_: Optional[str | Any] = None,
    rows: Optional[int | Any] = None,
    start: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search the Smithsonian Institution's open access collection of 5M+ digitized artifacts, specimens...

    Parameters
    ----------
    q : str
        Search query. Examples: 'dinosaur fossil', 'lunar module', 'butterflies', 'Wr...
    unit_code : str | Any
        Filter by museum/unit. Examples: 'NMNH' (Natural History), 'NASM' (Air & Spac...
    type_ : str | Any
        Object type filter. Examples: 'edanmdm:nasm_A19610048000' (specific item), or...
    rows : int | Any
        Number of results to return (default 10, max 100)
    start : int | Any
        Start offset for pagination
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
            "name": "Smithsonian_search_collection",
            "arguments": {
                "q": q,
                "unit_code": unit_code,
                "type": type_,
                "rows": rows,
                "start": start,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Smithsonian_search_collection"]
