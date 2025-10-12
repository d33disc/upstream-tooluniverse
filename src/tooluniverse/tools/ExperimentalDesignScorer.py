"""
ExperimentalDesignScorer

Assesses a proposed experimental design by assigning scores and structured feedback on hypothesis clarity, variable definitions, sample size, controls, randomization, measurement methods, statistical analysis, bias mitigation, ethical considerations, and overall feasibility.
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


def ExperimentalDesignScorer(
    hypothesis: str,
    design_description: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Assesses a proposed experimental design by assigning scores and structured feedback on hypothesis clarity, variable definitions, sample size, controls, randomization, measurement methods, statistical analysis, bias mitigation, ethical considerations, and overall feasibility.

    Parameters
    ----------
    hypothesis : str
        A clear statement of the research hypothesis to be tested.
    design_description : str
        A detailed description of the proposed experimental design, including variables, methods, sample details, and planned analyses.
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
            "name": "ExperimentalDesignScorer",
            "arguments": {
                "hypothesis": hypothesis,
                "design_description": design_description,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ExperimentalDesignScorer"]
