"""
DogCEO_get_sub_breeds

List all sub-breeds for a specific dog breed from the Dog CEO API. For example, 'bulldog' has sub...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def DogCEO_get_sub_breeds(
    breed: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    List all sub-breeds for a specific dog breed from the Dog CEO API. For example, 'bulldog' has sub...

    Parameters
    ----------
    breed : str
        Main breed name (lowercase). Examples: 'bulldog', 'hound', 'terrier', 'spanie...
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
        {"name": "DogCEO_get_sub_breeds", "arguments": {"breed": breed}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["DogCEO_get_sub_breeds"]
