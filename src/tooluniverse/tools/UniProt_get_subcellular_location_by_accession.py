"""
UniProt_get_subcellular_location_by_accession

Extract subcellular localization annotations from UniProtKB entry (Comment type = SUBCELLULAR LOCATION).
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


def UniProt_get_subcellular_location_by_accession(
    accession: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Extract subcellular localization annotations from UniProtKB entry (Comment type = SUBCELLULAR LOCATION).

    Parameters
    ----------
    accession : str
        UniProtKB accession, e.g., P05067.
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
            "name": "UniProt_get_subcellular_location_by_accession",
            "arguments": {"accession": accession},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["UniProt_get_subcellular_location_by_accession"]
