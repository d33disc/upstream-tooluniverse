"""
OSDR_search_studies

Search NASA's Open Science Data Repository (OSDR, formerly GeneLab) for space biology and life sc...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OSDR_search_studies(
    qs: str,
    type_: Optional[str] = "cgene",
    size: Optional[int] = 10,
    from_: Optional[int] = 0,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search NASA's Open Science Data Repository (OSDR, formerly GeneLab) for space biology and life sc...

    Parameters
    ----------
    qs : str
        Search query (e.g., 'microgravity', 'radiation', 'bone loss', 'muscle atrophy...
    type_ : str
        Data source type. Options: 'cgene' (all GeneLab), 'nih_geo_gse' (GEO), 'ebi_p...
    size : int
        Number of results to return (default 10)
    from_ : int
        Offset for pagination (default 0)
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
            "name": "OSDR_search_studies",
            "arguments": {"qs": qs, "type": type_, "size": size, "from": from_},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OSDR_search_studies"]
