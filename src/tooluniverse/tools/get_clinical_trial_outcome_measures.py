"""
get_clinical_trial_outcome_measures

Retrieves the outcome measures for the clinical trials, using their NCT IDs.
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


def get_clinical_trial_outcome_measures(
    nct_ids: Optional[list[Any]] = None,
    outcome_measures: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieves the outcome measures for the clinical trials, using their NCT IDs.

    Parameters
    ----------
    nct_ids : list[Any]
        List of NCT IDs of the clinical trials (e.g., ['NCT04852770', 'NCT01728545']).
    outcome_measures : str
        Decides whether to retrieve primary, secondary, or all outcome measures. Options are 'primary', 'secondary', or 'all'. Default is 'primary'.
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
            "name": "get_clinical_trial_outcome_measures",
            "arguments": {"nct_ids": nct_ids, "outcome_measures": outcome_measures},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["get_clinical_trial_outcome_measures"]
