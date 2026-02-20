"""
SECEDGAR_get_company_facts

Get structured financial data (XBRL facts) for a public company from SEC EDGAR using its CIK numb...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def SECEDGAR_get_company_facts(
    cik: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get structured financial data (XBRL facts) for a public company from SEC EDGAR using its CIK numb...

    Parameters
    ----------
    cik : str
        Company CIK (Central Index Key) number. Must be 10 digits (pad with zeros). E...
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
        {"name": "SECEDGAR_get_company_facts", "arguments": {"cik": cik}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["SECEDGAR_get_company_facts"]
