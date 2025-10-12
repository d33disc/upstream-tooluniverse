"""
CallAgent

Give a solution plan to the agent and let it solve the problem. Solution plan should reflect a distinct method, approach, or viewpoint to solve the given question. Call these function multiple times, and each solution plan should start with different aspects of the question, for example, genes, phenotypes, diseases, or drugs, etc. The CallAgent will achieve the task based on the plan, so only give the plan instead of unverified information.
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


def CallAgent(
    solution: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Give a solution plan to the agent and let it solve the problem. Solution plan should reflect a distinct method, approach, or viewpoint to solve the given question. Call these function multiple times, and each solution plan should start with different aspects of the question, for example, genes, phenotypes, diseases, or drugs, etc. The CallAgent will achieve the task based on the plan, so only give the plan instead of unverified information.

    Parameters
    ----------
    solution : str
        A feasible and concise solution plan that address the question.
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
        {"name": "CallAgent", "arguments": {"solution": solution}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["CallAgent"]
