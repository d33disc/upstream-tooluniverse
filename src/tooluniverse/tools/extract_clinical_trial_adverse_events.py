"""
extract_clinical_trial_adverse_events

Extracts detailed adverse event results from clinicaltrials.gov, using their NCT IDs.
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


def extract_clinical_trial_adverse_events(
    nct_ids: Optional[list[Any]] = None,
    organ_systems: Optional[list[Any]] = None,
    adverse_event_type: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Extracts detailed adverse event results from clinicaltrials.gov, using their NCT IDs.

    Parameters
    ----------
    nct_ids : list[Any]
        List of NCT IDs of the clinical trials (e.g., ['NCT04852770', 'NCT01728545']).
    organ_systems : list[Any]
        List of organs or organ systems to filter adverse events (see enum for exact text). Adverse events will be matched only if the input exactly matches their terms (case agnostic). If not specified, all adverse events will be returned. By default, all adverse events will be returned.
    adverse_event_type : str
        Type of adverse events to extract. Options are 'serious' (serious adverse events only), 'other' (non-serious adverse events only), 'all' (all adverse events), or specific event names such as 'nausea', 'neutropenia', 'epilepsy' (from MedDRA). For specific event names, adverse events will be matched as long as the input partially matches their terms (case agnostic). Querying for specific adverse event names is recommended as there are typically many adverse events logged. If querying for specific event names does not return any results, this parameter should be set to 'serious' for sanity check. By default, the value is set to 'serious', i.e. the tool will extract all serious adverse events.
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
            "name": "extract_clinical_trial_adverse_events",
            "arguments": {
                "nct_ids": nct_ids,
                "organ_systems": organ_systems,
                "adverse_event_type": adverse_event_type,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["extract_clinical_trial_adverse_events"]
