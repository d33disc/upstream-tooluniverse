"""
PubChem_get_compound_xrefs_by_CID

Get external references (XRefs) for compound by CID, including links to ChEBI, DrugBank, KEGG, etc.
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


def PubChem_get_compound_xrefs_by_CID(
    cid: int,
    xref_types: list[Any],
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get external references (XRefs) for compound by CID, including links to ChEBI, DrugBank, KEGG, etc.

    Parameters
    ----------
    cid : int
        Compound ID to query external references for, e.g., 2244.
    xref_types : list[Any]
        List of external database types to query, e.g., ["RegistryID", "RN", "PubMedID"].
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
            "name": "PubChem_get_compound_xrefs_by_CID",
            "arguments": {"cid": cid, "xref_types": xref_types},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["PubChem_get_compound_xrefs_by_CID"]
