"""
FDA_get_drug_names_by_application_number_NDC_number

Retrieve drug names based on the specified FDA application number or National Drug Code (NDC) number.
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


def FDA_get_drug_names_by_application_number_NDC_number(
    application_manufacturer_or_NDC_info: Optional[str] = None,
    limit: Optional[int] = None,
    skip: Optional[int] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve drug names based on the specified FDA application number or National Drug Code (NDC) number.

    Parameters
    ----------
    application_manufacturer_or_NDC_info : str
        FDA application, manufacturer, or NDC number info
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
            "name": "FDA_get_drug_names_by_application_number_NDC_number",
            "arguments": {
                "application_manufacturer_or_NDC_info": application_manufacturer_or_NDC_info,
                "limit": limit,
                "skip": skip,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["FDA_get_drug_names_by_application_number_NDC_number"]
