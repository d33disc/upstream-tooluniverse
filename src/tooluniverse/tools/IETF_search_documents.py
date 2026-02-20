"""
IETF_search_documents

Search for Internet standards documents (RFCs, Internet-Drafts) in the IETF Datatracker, the offi...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def IETF_search_documents(
    name__contains: Optional[str | Any] = None,
    title__contains: Optional[str | Any] = None,
    limit: Optional[int | Any] = None,
    offset: Optional[int | Any] = None,
    name__startswith: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for Internet standards documents (RFCs, Internet-Drafts) in the IETF Datatracker, the offi...

    Parameters
    ----------
    name__contains : str | Any
        Search by document name/number. Examples: 'rfc9110' (HTTP Semantics), 'rfc723...
    title__contains : str | Any
        Search by title keyword. Examples: 'HTTP', 'TLS', 'JSON', 'DNS', 'OAuth', 'We...
    limit : int | Any
        Number of results (1-100). Default: 20
    offset : int | Any
        Offset for pagination. Default: 0
    name__startswith : str | Any
        Filter documents whose name starts with this prefix. Use 'rfc' to only get RF...
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
            "name": "IETF_search_documents",
            "arguments": {
                "name__contains": name__contains,
                "title__contains": title__contains,
                "limit": limit,
                "offset": offset,
                "name__startswith": name__startswith,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["IETF_search_documents"]
