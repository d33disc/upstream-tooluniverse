"""
CollegeScorecard_search_schools

Search for US higher education institutions using the US Department of Education's College Scorec...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def CollegeScorecard_search_schools(
    school_name: Optional[str | Any] = None,
    school_state: Optional[str | Any] = None,
    school_type: Optional[int | Any] = None,
    fields: Optional[str | Any] = None,
    per_page: Optional[int | Any] = None,
    page: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for US higher education institutions using the US Department of Education's College Scorec...

    Parameters
    ----------
    school_name : str | Any
        Search by school name (partial match). Examples: 'Harvard', 'MIT', 'Stanford'...
    school_state : str | Any
        Filter by US state (2-letter abbreviation). Examples: 'CA', 'NY', 'TX', 'MA'
    school_type : int | Any
        School ownership type: 1=Public, 2=Private nonprofit, 3=Private for-profit
    fields : str | Any
        Comma-separated fields to return. Default returns key metrics. Options includ...
    per_page : int | Any
        Results per page (default 20, max 100)
    page : int | Any
        Page number for pagination
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
            "name": "CollegeScorecard_search_schools",
            "arguments": {
                "school_name": school_name,
                "school_state": school_state,
                "school_type": school_type,
                "fields": fields,
                "per_page": per_page,
                "page": page,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["CollegeScorecard_search_schools"]
