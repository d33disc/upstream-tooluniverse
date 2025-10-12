"""
get_pyfaidx_info

Get comprehensive information about pyfaidx – efficient FASTA file indexing and random access
"""

from typing import Any, Optional, Callable
from tooluniverse import ToolUniverse

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = ToolUniverse()
        _client.load_tools()
    return _client


def get_pyfaidx_info(
    include_examples: Optional[bool] = True,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get comprehensive information about pyfaidx – efficient FASTA file indexing and random access

    Parameters
    ----------
    include_examples : bool
        Whether to include usage examples and quick start guide
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
    return _get_client().run_one_function(
        {
            "name": "get_pyfaidx_info",
            "arguments": {"include_examples": include_examples},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["get_pyfaidx_info"]
