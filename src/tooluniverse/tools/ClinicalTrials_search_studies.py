"""
ClinicalTrials_search_studies

Search ClinicalTrials.gov for clinical trials and interventional/observational studies. Returns s...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def ClinicalTrials_search_studies(
    query_cond: Optional[str | Any] = None,
    query_intr: Optional[str | Any] = None,
    query_term: Optional[str | Any] = None,
    filter_overallStatus: Optional[str | Any] = None,
    filter_phase: Optional[str | Any] = None,
    pageSize: Optional[int | Any] = None,
    pageToken: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search ClinicalTrials.gov for clinical trials and interventional/observational studies. Returns s...

    Parameters
    ----------
    query_cond : str | Any
        Search condition/disease. Examples: 'diabetes', 'breast cancer', 'COVID-19', ...
    query_intr : str | Any
        Search intervention/treatment. Examples: 'metformin', 'immunotherapy', 'CRISP...
    query_term : str | Any
        General text search across all fields. Examples: 'BRCA1', 'phase 3 trial', 'p...
    filter_overallStatus : str | Any
        Filter by status. Values: 'RECRUITING', 'COMPLETED', 'ACTIVE_NOT_RECRUITING',...
    filter_phase : str | Any
        Filter by phase. Values: 'PHASE1', 'PHASE2', 'PHASE3', 'PHASE4', 'NA' (not ap...
    pageSize : int | Any
        Number of results per page (default 10, max 1000)
    pageToken : str | Any
        Token for next page from previous response
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
    # Handle mutable defaults to avoid B006 linting error

    return get_shared_client().run_one_function(
        {
            "name": "ClinicalTrials_search_studies",
            "arguments": {
                "query.cond": query_cond,
                "query.intr": query_intr,
                "query.term": query_term,
                "filter.overallStatus": filter_overallStatus,
                "filter.phase": filter_phase,
                "pageSize": pageSize,
                "pageToken": pageToken,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ClinicalTrials_search_studies"]
