"""
FourDN_get_experiment_metadata

Get metadata for 4DN experiments including experimental design, biosource information, protocol d...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def FourDN_get_experiment_metadata(
    operation: str,
    experiment_accession: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Get metadata for 4DN experiments including experimental design, biosource information, protocol d...

    Parameters
    ----------
    operation : str

    experiment_accession : str
        4DN experiment accession (e.g., '4DNEXO67APU1')
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
            "name": "FourDN_get_experiment_metadata",
            "arguments": {
                "operation": operation,
                "experiment_accession": experiment_accession,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["FourDN_get_experiment_metadata"]
