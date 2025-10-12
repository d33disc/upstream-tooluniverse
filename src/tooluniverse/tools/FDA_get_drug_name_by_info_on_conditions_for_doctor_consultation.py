"""
FDA_get_drug_name_by_info_on_conditions_for_doctor_consultation

Retrieve the drug names that require asking a doctor before use due to a patient's specific conditions and symptoms.  Warning: This tool only outputs a predefined limited number of drug names and does not cover all possible drugs. Use with caution.
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


def FDA_get_drug_name_by_info_on_conditions_for_doctor_consultation(
    condition: Optional[str] = None,
    limit: Optional[int] = None,
    skip: Optional[int] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve the drug names that require asking a doctor before use due to a patient's specific conditions and symptoms.  Warning: This tool only outputs a predefined limited number of drug names and does not cover all possible drugs. Use with caution.

    Parameters
    ----------
    condition : str
        The condition or symptom that requires consulting a doctor.
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
            "name": "FDA_get_drug_name_by_info_on_conditions_for_doctor_consultation",
            "arguments": {"condition": condition, "limit": limit, "skip": skip},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["FDA_get_drug_name_by_info_on_conditions_for_doctor_consultation"]
