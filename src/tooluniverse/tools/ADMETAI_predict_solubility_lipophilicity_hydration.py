"""
ADMETAI_predict_solubility_lipophilicity_hydration

Predicts solubility, lipophilicity, and hydration endpoints (Solubility_AqSolDB, Lipophilicity_AstraZeneca, HydrationFreeEnergy_FreeSolv) for a given list of molecules in SMILES format.
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


def ADMETAI_predict_solubility_lipophilicity_hydration(
    smiles: list[Any],
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Predicts solubility, lipophilicity, and hydration endpoints (Solubility_AqSolDB, Lipophilicity_AstraZeneca, HydrationFreeEnergy_FreeSolv) for a given list of molecules in SMILES format.

    Parameters
    ----------
    smiles : list[Any]
        The list of SMILES strings.
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
            "name": "ADMETAI_predict_solubility_lipophilicity_hydration",
            "arguments": {"smiles": smiles},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ADMETAI_predict_solubility_lipophilicity_hydration"]
