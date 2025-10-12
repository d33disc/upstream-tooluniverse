"""
MedicalLiteratureReviewer

Conducts systematic reviews of medical literature on specific topics. Synthesizes findings from multiple studies and provides evidence-based conclusions with structured analysis and quality assessment.
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


def MedicalLiteratureReviewer(
    research_topic: str,
    literature_content: str,
    focus_area: str,
    study_types: str,
    quality_level: str,
    review_scope: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Conducts systematic reviews of medical literature on specific topics. Synthesizes findings from multiple studies and provides evidence-based conclusions with structured analysis and quality assessment.

    Parameters
    ----------
    research_topic : str
        The specific medical/research topic for literature review (e.g., 'efficacy of drug X in treating condition Y').
    literature_content : str
        The literature content, abstracts, full studies, or research papers to review and synthesize.
    focus_area : str
        Primary focus area for the review (e.g., 'therapeutic efficacy', 'safety profile', 'diagnostic accuracy', 'biomarker validation').
    study_types : str
        Types of studies to prioritize in the analysis (e.g., 'randomized controlled trials', 'meta-analyses', 'cohort studies', 'case-control studies').
    quality_level : str
        Minimum evidence quality level to include (e.g., 'high quality only', 'moderate and above', 'all available evidence').
    review_scope : str
        Scope of the review (e.g., 'comprehensive systematic review', 'rapid review', 'scoping review', 'narrative review').
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
            "name": "MedicalLiteratureReviewer",
            "arguments": {
                "research_topic": research_topic,
                "literature_content": literature_content,
                "focus_area": focus_area,
                "study_types": study_types,
                "quality_level": quality_level,
                "review_scope": review_scope,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["MedicalLiteratureReviewer"]
