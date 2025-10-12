"""
BiomarkerDiscoveryWorkflow

Discover and validate biomarkers for a specific disease condition using literature analysis, expression data, pathway enrichment, and clinical validation.
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


def BiomarkerDiscoveryWorkflow(
    disease_condition: str,
    sample_type: Optional[str] = "blood",
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Discover and validate biomarkers for a specific disease condition using literature analysis, expression data, pathway enrichment, and clinical validation.

    Parameters
    ----------
    disease_condition : str
        The disease condition to discover biomarkers for (e.g., 'breast cancer', 'Alzheimer's disease')
    sample_type : str
        The type of sample to analyze (e.g., 'blood', 'tissue', 'plasma')
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
            "name": "BiomarkerDiscoveryWorkflow",
            "arguments": {
                "disease_condition": disease_condition,
                "sample_type": sample_type,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["BiomarkerDiscoveryWorkflow"]
