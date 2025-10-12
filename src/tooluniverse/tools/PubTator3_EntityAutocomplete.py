"""
PubTator3_EntityAutocomplete

Provides suggestions for the best‐matching standardized PubTator IDs for a partial biomedical term (gene, disease, chemical, or variant). Use this tool first to convert free‐text names into the stable @IDs required by the other PubTator APIs.
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


def PubTator3_EntityAutocomplete(
    text: str,
    entity_type: Optional[str] = None,
    max_results: Optional[int] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Provides suggestions for the best‐matching standardized PubTator IDs for a partial biomedical term (gene, disease, chemical, or variant). Use this tool first to convert free‐text names into the stable @IDs required by the other PubTator APIs.

    Parameters
    ----------
    text : str
        A few characters or the full name of the biomedical concept you are trying to look up (e.g. “BRAF V6”).
    entity_type : str
        Optional filter to restrict suggestions to a single category such as GENE, DISEASE, CHEMICAL, or VARIANT.
    max_results : int
        Maximum number of suggestions to return (1 - 50, default = 10).
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
            "name": "PubTator3_EntityAutocomplete",
            "arguments": {
                "text": text,
                "entity_type": entity_type,
                "max_results": max_results,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["PubTator3_EntityAutocomplete"]
