"""
TreasuryFiscal_get_exchange_rates

Get US Treasury quarterly exchange rates for foreign currencies against the US dollar. The Treasu...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def TreasuryFiscal_get_exchange_rates(
    filter: Optional[str | Any] = None,
    sort: Optional[str | Any] = None,
    fields: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get US Treasury quarterly exchange rates for foreign currencies against the US dollar. The Treasu...

    Parameters
    ----------
    filter : str | Any
        Filter expression. Examples: 'country:eq:Canada', 'country:eq:Japan,record_da...
    sort : str | Any
        Sort field with optional '-' prefix for descending. Default: '-record_date'. ...
    fields : str | Any
        Comma-separated fields to return. Available: record_date, country, currency, ...
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
            "name": "TreasuryFiscal_get_exchange_rates",
            "arguments": {"filter": filter, "sort": sort, "fields": fields},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["TreasuryFiscal_get_exchange_rates"]
