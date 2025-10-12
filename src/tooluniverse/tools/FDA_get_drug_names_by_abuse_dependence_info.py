"""
FDA_get_drug_names_by_abuse_dependence_info

Retrieve the drug name based on information about drug abuse and dependence, including whether the drug is a controlled substances, the types of possible abuse, and adverse reactions relevant to those abuse types.
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


def FDA_get_drug_names_by_abuse_dependence_info(
    abuse_info: Optional[str] = None,
    limit: Optional[int] = None,
    skip: Optional[int] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve the drug name based on information about drug abuse and dependence, including whether the drug is a controlled substances, the types of possible abuse, and adverse reactions relevant to those abuse types.

    Parameters
    ----------
    abuse_info : str
        Information about drug abuse and dependence.
    limit : int
        The number of records to return.
    skip : int
        The number of records to skip.
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
    return _get_client().run_one_function(
        {
            "name": "FDA_get_drug_names_by_abuse_dependence_info",
            "arguments": {"abuse_info": abuse_info, "limit": limit, "skip": skip},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["FDA_get_drug_names_by_abuse_dependence_info"]
