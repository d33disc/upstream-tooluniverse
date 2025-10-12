"""
DailyMed_search_spls

Search SPL list using multiple filter conditions (drug_name/ndc/rxcui/setid) and return metadata + data array.
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


def DailyMed_search_spls(
    drug_name: Optional[str] = None,
    ndc: Optional[str] = None,
    rxcui: Optional[str] = None,
    setid: Optional[str] = None,
    published_date_gte: Optional[str] = None,
    published_date_eq: Optional[str] = None,
    pagesize: Optional[int] = 100,
    page: Optional[int] = 1,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search SPL list using multiple filter conditions (drug_name/ndc/rxcui/setid) and return metadata + data array.

    Parameters
    ----------
    drug_name : str
        Generic or brand name of the drug, e.g., 'TAMSULOSIN HYDROCHLORIDE'.
    ndc : str
        National Drug Code (NDC).
    rxcui : str
        RxNorm Code (RXCUI).
    setid : str
        Set ID corresponding to the SPL.
    published_date_gte : str
        Published date >= specified date, format 'YYYY-MM-DD'.
    published_date_eq : str
        Published date == specified date, format 'YYYY-MM-DD'.
    pagesize : int
        Number of items per page, maximum 100, default 100.
    page : int
        Page number, starts from 1, default 1.
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
            "name": "DailyMed_search_spls",
            "arguments": {
                "drug_name": drug_name,
                "ndc": ndc,
                "rxcui": rxcui,
                "setid": setid,
                "published_date_gte": published_date_gte,
                "published_date_eq": published_date_eq,
                "pagesize": pagesize,
                "page": page,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["DailyMed_search_spls"]
