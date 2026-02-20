"""
SECEDGAR_search_filings

Search SEC EDGAR full-text for regulatory filings (10-K, 10-Q, 8-K, DEF 14A, etc.) from publicly ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def SECEDGAR_search_filings(
    q: str,
    forms: Optional[str | Any] = None,
    dateRange: Optional[str | Any] = None,
    startdt: Optional[str | Any] = None,
    enddt: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search SEC EDGAR full-text for regulatory filings (10-K, 10-Q, 8-K, DEF 14A, etc.) from publicly ...

    Parameters
    ----------
    q : str
        Full-text search query. Examples: 'climate change risk', 'artificial intellig...
    forms : str | Any
        Filter by form type(s), comma-separated. Examples: '10-K' (annual report), '1...
    dateRange : str | Any
        Date range filter. Values: 'custom' (use with startdt/enddt). Examples: 'custom'
    startdt : str | Any
        Start date filter (YYYY-MM-DD). Example: '2024-01-01'
    enddt : str | Any
        End date filter (YYYY-MM-DD). Example: '2024-12-31'
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
            "name": "SECEDGAR_search_filings",
            "arguments": {
                "q": q,
                "forms": forms,
                "dateRange": dateRange,
                "startdt": startdt,
                "enddt": enddt,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["SECEDGAR_search_filings"]
