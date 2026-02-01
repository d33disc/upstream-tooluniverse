"""
FourDN_get_download_url

Get download URL and DRS (Data Repository Service) API endpoint for 4DN files. Prerequisites: Req...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def FourDN_get_download_url(
    operation: str,
    file_accession: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Get download URL and DRS (Data Repository Service) API endpoint for 4DN files. Prerequisites: Req...

    Parameters
    ----------
    operation : str

    file_accession : str
        4DN file accession
    stream_callback : Callable, optional
        Callback for streaming output
    use_cache : bool, default False
        Enable caching
    validate : bool, default True
        Validate parameters

    Returns
    -------
    dict[str, Any]
    """
    # Handle mutable defaults to avoid B006 linting error

    return get_shared_client().run_one_function(
        {
            "name": "FourDN_get_download_url",
            "arguments": {"operation": operation, "file_accession": file_accession},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["FourDN_get_download_url"]
