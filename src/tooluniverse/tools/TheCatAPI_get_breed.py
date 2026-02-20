"""
TheCatAPI_get_breed

Get detailed information about a specific cat breed by its ID from TheCatAPI. Returns comprehensi...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def TheCatAPI_get_breed(
    breed_id: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get detailed information about a specific cat breed by its ID from TheCatAPI. Returns comprehensi...

    Parameters
    ----------
    breed_id : str
        Breed ID code (e.g., 'abys' for Abyssinian, 'pers' for Persian, 'siam' for Si...
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
        {"name": "TheCatAPI_get_breed", "arguments": {"breed_id": breed_id}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["TheCatAPI_get_breed"]
