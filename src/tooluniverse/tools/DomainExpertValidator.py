"""
DomainExpertValidator

Provides domain-specific validation and expert recommendations for tools with deep expertise across scientific and technical domains
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


def DomainExpertValidator(
    tool_config: str,
    domain: str,
    validation_aspects: Optional[str] = '["accuracy", "methodology", "best-practices"]',
    implementation_code: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Provides domain-specific validation and expert recommendations for tools with deep expertise across scientific and technical domains

    Parameters
    ----------
    tool_config : str
        JSON string of tool configuration to validate
    domain : str
        Domain expertise area for validation
    validation_aspects : str
        JSON array string of specific aspects to validate
    implementation_code : str
        Implementation code to validate (optional)
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
            "name": "DomainExpertValidator",
            "arguments": {
                "tool_config": tool_config,
                "domain": domain,
                "validation_aspects": validation_aspects,
                "implementation_code": implementation_code,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["DomainExpertValidator"]
