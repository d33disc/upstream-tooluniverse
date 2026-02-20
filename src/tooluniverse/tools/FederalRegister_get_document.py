"""
FederalRegister_get_document

Get detailed information about a specific Federal Register document by its document number. Retur...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def FederalRegister_get_document(
    document_number: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get detailed information about a specific Federal Register document by its document number. Retur...

    Parameters
    ----------
    document_number : str
        Federal Register document number (e.g., '2025-06701', '2024-12345'). Found in...
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
            "name": "FederalRegister_get_document",
            "arguments": {"document_number": document_number},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["FederalRegister_get_document"]
