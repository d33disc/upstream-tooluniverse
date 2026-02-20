"""
CratesIO_get_crate

Get detailed information about a specific Rust crate from crates.io including version history, do...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def CratesIO_get_crate(
    crate_name: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get detailed information about a specific Rust crate from crates.io including version history, do...

    Parameters
    ----------
    crate_name : str
        Exact crate name. Examples: 'tokio', 'serde', 'reqwest', 'actix-web', 'clap',...
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
        {"name": "CratesIO_get_crate", "arguments": {"crate_name": crate_name}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["CratesIO_get_crate"]
