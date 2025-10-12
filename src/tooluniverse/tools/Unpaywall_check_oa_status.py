"""
Unpaywall_check_oa_status

Query Unpaywall by DOI to check open-access status and OA locations. Requires a contact email for API access.
"""

from typing import Any, Optional, Callable
from tooluniverse import ToolUniverse

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = ToolUniverse()
        _client.load_tools()
    return _client


def Unpaywall_check_oa_status(
    doi: str,
    email: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Query Unpaywall by DOI to check open-access status and OA locations. Requires a contact email for API access.

    Parameters
    ----------
    doi : str
        DOI (Digital Object Identifier) of the article to check for open access status.
    email : str
        Contact email address required by Unpaywall API for polite usage tracking.
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
    return _get_client().run_one_function(
        {
            "name": "Unpaywall_check_oa_status",
            "arguments": {"doi": doi, "email": email},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Unpaywall_check_oa_status"]
