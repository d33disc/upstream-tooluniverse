"""
PubChem_get_CID_by_SMILES

Retrieve corresponding CID list by SMILES string.
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


def PubChem_get_CID_by_SMILES(
    smiles: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve corresponding CID list by SMILES string.

    Parameters
    ----------
    smiles : str
        SMILES expression (e.g., "CC(=O)OC1=CC=CC=C1C(=O)O" corresponds to aspirin).
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
        {"name": "PubChem_get_CID_by_SMILES", "arguments": {"smiles": smiles}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["PubChem_get_CID_by_SMILES"]
