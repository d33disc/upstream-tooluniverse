"""
TreasuryFiscal_get_national_debt

Get the US total public debt outstanding (debt to the penny) from the US Treasury Fiscal Data API...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def TreasuryFiscal_get_national_debt(
    filter: Optional[str | Any] = None,
    sort: Optional[str | Any] = None,
    fields: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get the US total public debt outstanding (debt to the penny) from the US Treasury Fiscal Data API...

    Parameters
    ----------
    filter : str | Any
        Filter expression in format 'field:operator:value'. Examples: 'record_date:gt...
    sort : str | Any
        Sort field, prefix with '-' for descending. Default: '-record_date' (newest f...
    fields : str | Any
        Comma-separated list of fields to return. Available: record_date, debt_held_p...
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
            "name": "TreasuryFiscal_get_national_debt",
            "arguments": {"filter": filter, "sort": sort, "fields": fields},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["TreasuryFiscal_get_national_debt"]
