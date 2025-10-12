"""
get_clinical_trial_eligibility_criteria

Retrieves the eligibility criteria for the clinical trials, using their NCT IDs.
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


def get_clinical_trial_eligibility_criteria(
    nct_ids: Optional[list[Any]] = None,
    eligibility_criteria: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieves the eligibility criteria for the clinical trials, using their NCT IDs.

    Parameters
    ----------
    nct_ids : list[Any]
        List of NCT IDs of the clinical trials (e.g., ['NCT04852770', 'NCT01728545']).
    eligibility_criteria : str
        Placeholder.
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
            "name": "get_clinical_trial_eligibility_criteria",
            "arguments": {
                "nct_ids": nct_ids,
                "eligibility_criteria": eligibility_criteria,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["get_clinical_trial_eligibility_criteria"]
