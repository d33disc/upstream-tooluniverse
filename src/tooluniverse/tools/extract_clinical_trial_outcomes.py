"""
extract_clinical_trial_outcomes

Extracts detailed trial outcome results (e.g., overall survival months, p-values, etc.) from clinicaltrials.gov, using their NCT IDs.
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


def extract_clinical_trial_outcomes(
    nct_ids: Optional[list[Any]] = None,
    outcome_measure: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Extracts detailed trial outcome results (e.g., overall survival months, p-values, etc.) from clinicaltrials.gov, using their NCT IDs.

    Parameters
    ----------
    nct_ids : list[Any]
        List of NCT IDs of the clinical trials (e.g., ['NCT04852770', 'NCT01728545']).
    outcome_measure : str
        Outcome measure to extract. Example values include 'primary' (primary outcomes only), 'secondary' (secondary outcomes only), 'all' (all outcomes), or specific measure names such as 'survival', 'overall survival'. For specific measure names, outcome measures will be matched as long as the input partially matches their titles or descriptions (case agnostic). Querying for specific measure names is recommended after getting an overview of outcome measures ('primary'). If querying for specific measure names does not return any results, this parameter should be set to 'primary' for sanity check. By default, the value is set to 'primary', i.e. the tool will extract all primary outcome results.
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
            "name": "extract_clinical_trial_outcomes",
            "arguments": {"nct_ids": nct_ids, "outcome_measure": outcome_measure},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["extract_clinical_trial_outcomes"]
