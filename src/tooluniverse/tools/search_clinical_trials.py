"""
search_clinical_trials

Search for clinical trials registered on clinicaltrials.gov based on title, conditions, interventions, outcome measures, and status. Returns a paginated list of studies, containing the NCT ID and description of each trial. You can then take the NCT IDs and use 'get_clinical_trials_*' tools to get detailed information about specific protocol fields for specific studies, or 'extract_clinical_trials_efficacy/safety' tools to get efficacy or adverse events results from specific studies. If you wish to see the next page of results, you can use the 'nextPageToken' value from the previous output of this tool and input it as the 'pageToken' parameter in the next query. Note that currently the search is limited to trials beyond phase 1.
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


def search_clinical_trials(
    condition: Optional[str] = None,
    intervention: Optional[str] = None,
    query_term: Optional[str] = None,
    pageSize: Optional[int] = None,
    pageToken: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for clinical trials registered on clinicaltrials.gov based on title, conditions, interventions, outcome measures, and status. Returns a paginated list of studies, containing the NCT ID and description of each trial. You can then take the NCT IDs and use 'get_clinical_trials_*' tools to get detailed information about specific protocol fields for specific studies, or 'extract_clinical_trials_efficacy/safety' tools to get efficacy or adverse events results from specific studies. If you wish to see the next page of results, you can use the 'nextPageToken' value from the previous output of this tool and input it as the 'pageToken' parameter in the next query. Note that currently the search is limited to trials beyond phase 1.

    Parameters
    ----------
    condition : str
        Query for condition or disease using Essie expression syntax (e.g., 'lung cancer', '(head OR neck) AND pain AND NOT "back pain"').
    intervention : str
        Query for intervention/treatment using Essie expression syntax (e.g., 'chemotherapy', 'immunotherapy', 'olaparib', 'combination therapy').
    query_term : str
        Query for 'other terms' with Essie expression syntax (e.g., 'combination', 'AREA[LastUpdatePostDate]RANGE[2023-01-15,MAX]', 'Phase II'). Can be used to search for all other protocol fields, including but not limited to title, outcome measures, status, phase, location, etc.
    pageSize : int
        Maximum number of studies to return per page (default 10, max 1000).
    pageToken : str
        Token to retrieve the next page of results, obtained from the 'nextPageToken' field of the previous response. Do not specify it for first page. When you make an initial request to the API which supports pagination, the response will include a nextPageToken. This token can then be used as a parameter in the subsequent API request to retrieve the next set of data.
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
            "name": "search_clinical_trials",
            "arguments": {
                "condition": condition,
                "intervention": intervention,
                "query_term": query_term,
                "pageSize": pageSize,
                "pageToken": pageToken,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["search_clinical_trials"]
