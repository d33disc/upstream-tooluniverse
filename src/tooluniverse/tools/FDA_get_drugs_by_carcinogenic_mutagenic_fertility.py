"""
FDA_get_drugs_by_carcinogenic_mutagenic_fertility

Retrieve drug names based on the presence of carcinogenic, mutagenic, or fertility impairment information.
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


def FDA_get_drugs_by_carcinogenic_mutagenic_fertility(
    carcinogenic_info: Optional[str] = None,
    indication: Optional[str] = None,
    limit: Optional[int] = None,
    skip: Optional[int] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve drug names based on the presence of carcinogenic, mutagenic, or fertility impairment information.

    Parameters
    ----------
    carcinogenic_info : str
        Information about carcinogenic, mutagenic, or fertility impairment potential.
    indication : str
        The indication or usage of the drug.
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
            "name": "FDA_get_drugs_by_carcinogenic_mutagenic_fertility",
            "arguments": {
                "carcinogenic_info": carcinogenic_info,
                "indication": indication,
                "limit": limit,
                "skip": skip,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["FDA_get_drugs_by_carcinogenic_mutagenic_fertility"]
