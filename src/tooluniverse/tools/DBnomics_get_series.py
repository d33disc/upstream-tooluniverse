"""
DBnomics_get_series

Get time series data (observations) from DBnomics. Returns actual data values with time periods f...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def DBnomics_get_series(
    provider_code: str,
    dataset_code: str,
    series_code: str,
    observations: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get time series data (observations) from DBnomics. Returns actual data values with time periods f...

    Parameters
    ----------
    provider_code : str
        Provider code (e.g., 'IMF', 'Eurostat', 'OECD', 'WorldBank', 'ECB', 'BLS')
    dataset_code : str
        Dataset code within the provider (e.g., 'WEO:2024-10', 'CPIH01')
    series_code : str
        Series code within the dataset (e.g., 'USA.NGDP_RPCH.pcent_change' for US GDP...
    observations : int | Any
        Set to 1 to include data observations (period and value arrays). Default: 0 (...
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
            "name": "DBnomics_get_series",
            "arguments": {
                "provider_code": provider_code,
                "dataset_code": dataset_code,
                "series_code": series_code,
                "observations": observations,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["DBnomics_get_series"]
