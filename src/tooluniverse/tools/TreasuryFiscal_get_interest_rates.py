"""
TreasuryFiscal_get_interest_rates

Get average interest rates on US Treasury securities (Bills, Notes, Bonds, TIPS, FRNs). Published...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def TreasuryFiscal_get_interest_rates(
    filter: Optional[str | Any] = None,
    sort: Optional[str | Any] = None,
    fields: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get average interest rates on US Treasury securities (Bills, Notes, Bonds, TIPS, FRNs). Published...

    Parameters
    ----------
    filter : str | Any
        Filter expression. Examples: 'security_desc:eq:Treasury Notes', 'record_date:...
    sort : str | Any
        Sort field with optional '-' prefix for descending. Default: '-record_date'.
    fields : str | Any
        Comma-separated fields. Available: record_date, security_type_desc, security_...
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
            "name": "TreasuryFiscal_get_interest_rates",
            "arguments": {"filter": filter, "sort": sort, "fields": fields},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["TreasuryFiscal_get_interest_rates"]
