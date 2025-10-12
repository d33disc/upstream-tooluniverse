"""
OSL_get_efo_id_by_disease_name

Tool to lookup Experimental Factor Ontology (EFO) IDs for diseases via the EMBL-EBI OLS API.
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


def OSL_get_efo_id_by_disease_name(
    disease: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Tool to lookup Experimental Factor Ontology (EFO) IDs for diseases via the EMBL-EBI OLS API.

    Parameters
    ----------
    disease : str
        Search query for diseases. Provide the disease name to lookup the corresponding EFO ID.
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
        {"name": "OSL_get_efo_id_by_disease_name", "arguments": {"disease": disease}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OSL_get_efo_id_by_disease_name"]
