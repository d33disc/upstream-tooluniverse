"""
FederalRegister_search_documents

Search the U.S. Federal Register for government documents including rules, proposed rules, notice...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def FederalRegister_search_documents(
    term: str,
    per_page: Optional[int | Any] = None,
    page: Optional[int | Any] = None,
    document_type: Optional[str | Any] = None,
    agency: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search the U.S. Federal Register for government documents including rules, proposed rules, notice...

    Parameters
    ----------
    term : str
        Search term (e.g., 'artificial intelligence', 'climate change', 'drug safety'...
    per_page : int | Any
        Results per page (1-1000). Default: 20
    page : int | Any
        Page number for pagination. Default: 1
    document_type : str | Any
        Document type filter. Options: 'RULE' (final rules), 'PRORULE' (proposed rule...
    agency : str | Any
        Filter by agency slug (e.g., 'environmental-protection-agency', 'food-and-dru...
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
            "name": "FederalRegister_search_documents",
            "arguments": {
                "term": term,
                "per_page": per_page,
                "page": page,
                "document_type": document_type,
                "agency": agency,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["FederalRegister_search_documents"]
