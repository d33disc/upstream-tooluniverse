"""
ComprehensiveDrugDiscoveryPipeline

Complete end-to-end drug discovery workflow from disease to optimized candidates. Identifies targets, discovers lead compounds, screens for ADMET properties, assesses safety, and validates with literature.
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


def ComprehensiveDrugDiscoveryPipeline(
    disease_efo_id: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Complete end-to-end drug discovery workflow from disease to optimized candidates. Identifies targets, discovers lead compounds, screens for ADMET properties, assesses safety, and validates with literature.

    Parameters
    ----------
    disease_efo_id : str
        The EFO ID of the disease for drug discovery (e.g., 'EFO_0001074' for Alzheimer's disease)
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
            "name": "ComprehensiveDrugDiscoveryPipeline",
            "arguments": {"disease_efo_id": disease_efo_id},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ComprehensiveDrugDiscoveryPipeline"]
