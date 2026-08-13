"""
USPTO_download_bulk_dataset_file

Download a bulk data product file from the USPTO BDSS. Returns the file content (CSV/XML, may be ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def USPTO_download_bulk_dataset_file(
    productIdentifier: str,
    fileName: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Download a bulk data product file from the USPTO BDSS. Returns the file content (CSV/XML, may be ...

    Parameters
    ----------
    productIdentifier : str
        Product identifier (shortName), e.g. 'PTGRXML'.
    fileName : str
        File name within the product, e.g. 'ipg200908.zip'.
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

    # Strip None values so optional parameters don't trigger schema validation errors
    _args = {
        k: v
        for k, v in {
            "productIdentifier": productIdentifier,
            "fileName": fileName,
        }.items()
        if v is not None
    }
    return get_shared_client().run_one_function(
        {
            "name": "USPTO_download_bulk_dataset_file",
            "arguments": _args,
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["USPTO_download_bulk_dataset_file"]
