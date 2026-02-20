"""
OSDR_get_study

Get detailed metadata for a specific study from NASA's Open Science Data Repository (OSDR). Retur...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OSDR_get_study(
    study_id: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get detailed metadata for a specific study from NASA's Open Science Data Repository (OSDR). Retur...

    Parameters
    ----------
    study_id : str
        Numeric study ID (e.g., '379', '137', '47', '120'). This is the number from O...
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
        {"name": "OSDR_get_study", "arguments": {"study_id": study_id}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OSDR_get_study"]
