"""
Lichess_get_top_players

Get the top 50 Lichess.org players for a specific time control using the Lichess public API. Retu...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Lichess_get_top_players(
    nb: int,
    perfType: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get the top 50 Lichess.org players for a specific time control using the Lichess public API. Retu...

    Parameters
    ----------
    nb : int
        Number of top players to return (1-200). Default: 10
    perfType : str
        Time control / performance type. Values: 'bullet', 'blitz', 'rapid', 'classic...
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
            "name": "Lichess_get_top_players",
            "arguments": {"nb": nb, "perfType": perfType},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Lichess_get_top_players"]
