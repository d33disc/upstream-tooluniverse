"""
DBnomics_get_dataset

Get detailed information about a specific DBnomics dataset including its dimensions, available va...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def DBnomics_get_dataset(
    provider_code: str,
    dataset_code: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get detailed information about a specific DBnomics dataset including its dimensions, available va...

    Parameters
    ----------
    provider_code : str
        Provider code (e.g., 'IMF', 'Eurostat', 'OECD', 'WorldBank', 'ECB')
    dataset_code : str
        Dataset code (e.g., 'WEO:2024-10' for IMF World Economic Outlook, 'GOV_10A_EX...
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
            "name": "DBnomics_get_dataset",
            "arguments": {"provider_code": provider_code, "dataset_code": dataset_code},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["DBnomics_get_dataset"]
