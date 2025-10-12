"""
get_sequence_positional_features_by_instance_id

Retrieve sequence positional features (e.g., binding sites, motifs) for a polymer entity instance.
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


def get_sequence_positional_features_by_instance_id(
    instance_id: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve sequence positional features (e.g., binding sites, motifs) for a polymer entity instance.

    Parameters
    ----------
    instance_id : str
        Polymer entity instance ID like '1NDO.A'
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
            "name": "get_sequence_positional_features_by_instance_id",
            "arguments": {"instance_id": instance_id},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["get_sequence_positional_features_by_instance_id"]
