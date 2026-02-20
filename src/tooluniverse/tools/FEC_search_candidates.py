"""
FEC_search_candidates

Search for US federal election candidates in the Federal Election Commission (FEC) database. Retu...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def FEC_search_candidates(
    name: Optional[str | Any] = None,
    party: Optional[str | Any] = None,
    office: Optional[str | Any] = None,
    state: Optional[str | Any] = None,
    election_year: Optional[int | Any] = None,
    per_page: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for US federal election candidates in the Federal Election Commission (FEC) database. Retu...

    Parameters
    ----------
    name : str | Any
        Candidate name search. Examples: 'Biden', 'Trump', 'Sanders', 'Warren'
    party : str | Any
        Party affiliation code. Examples: 'DEM' (Democrat), 'REP' (Republican), 'IND'...
    office : str | Any
        Office sought. Values: 'P' (President), 'S' (Senate), 'H' (House)
    state : str | Any
        State code for Senate/House candidates. Examples: 'CA', 'NY', 'TX'
    election_year : int | Any
        Election year. Examples: 2024, 2022, 2020
    per_page : int | Any
        Results per page (default 20, max 100)
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
            "name": "FEC_search_candidates",
            "arguments": {
                "name": name,
                "party": party,
                "office": office,
                "state": state,
                "election_year": election_year,
                "per_page": per_page,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["FEC_search_candidates"]
