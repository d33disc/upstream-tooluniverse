"""
FDA_get_drug_names_by_clinical_pharmacology

Retrieve drug names based on clinical pharmacology information. Warning: This tool only outputs a predefined limited number of drug names and does not cover all possible drugs. Use with caution.
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


def FDA_get_drug_names_by_clinical_pharmacology(
    clinical_pharmacology: Optional[str] = None,
    indication: Optional[str] = None,
    limit: Optional[int] = None,
    skip: Optional[int] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve drug names based on clinical pharmacology information. Warning: This tool only outputs a predefined limited number of drug names and does not cover all possible drugs. Use with caution.

    Parameters
    ----------
    clinical_pharmacology : str
        Information about the clinical pharmacology and actions of the drug in humans. Use key words
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
            "name": "FDA_get_drug_names_by_clinical_pharmacology",
            "arguments": {
                "clinical_pharmacology": clinical_pharmacology,
                "indication": indication,
                "limit": limit,
                "skip": skip,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["FDA_get_drug_names_by_clinical_pharmacology"]
