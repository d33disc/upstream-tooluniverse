"""
AdvancedCodeQualityAnalyzer

Performs deep analysis of code quality including complexity, security, performance, and maintainability metrics with domain-specific expertise
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


def AdvancedCodeQualityAnalyzer(
    source_code: str,
    language: Optional[str] = "python",
    analysis_depth: Optional[str] = "comprehensive",
    domain_context: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Performs deep analysis of code quality including complexity, security, performance, and maintainability metrics with domain-specific expertise

    Parameters
    ----------
    source_code : str
        The source code to analyze for quality assessment
    language : str
        Programming language (python, javascript, etc.)
    analysis_depth : str
        Level of analysis depth to perform
    domain_context : str
        Domain context for specialized analysis (e.g., bioinformatics, web development)
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
            "name": "AdvancedCodeQualityAnalyzer",
            "arguments": {
                "source_code": source_code,
                "language": language,
                "analysis_depth": analysis_depth,
                "domain_context": domain_context,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["AdvancedCodeQualityAnalyzer"]
