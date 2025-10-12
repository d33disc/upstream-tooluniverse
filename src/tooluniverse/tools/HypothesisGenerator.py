"""
HypothesisGenerator

Generates research hypotheses based on provided background context, domain, and desired format. Uses AI to propose novel, testable hypotheses for scientific exploration.
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


def HypothesisGenerator(
    context: str,
    domain: str,
    number_of_hypotheses: str,
    hypothesis_format: Optional[str] = "concise declarative sentences",
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
        Generates research hypotheses based on provided background context, domain, and desired format. Uses AI to propose novel, testable hypotheses for scientific exploration.

        Parameters
        ----------
        context : str
            Background information, observations, or data description from which to derive hypotheses.
        domain : str
            Field of study or research area (e.g., 'neuroscience', 'ecology', 'materials science').
        number_of_hypotheses : str
            Number of hypotheses to generate (e.g., '3', '5').
        hypothesis_format : str
            Optional directive on how to structure each hypothesis. Choose from one of the following formats:

    1. If–Then Statements: "If [independent variable condition], then [expected outcome]."
    2. Null and Alternative (Statistical):
       • H₀ (Null): "There is no difference/effect/association between X and Y."
       • H₁ (Alt): "There is a difference/effect/association between X and Y."
    3. Associative (Correlation-Focused): "There is a relationship/association between [Variable A] and [Variable B]."
    4. Directional (Non-If–Then): "Increasing/decreasing [Variable A] will lead to [directional change] in [Variable B]."
    5. Comparative (Group Comparison): "Group A will show higher/lower [dependent measure] compared to Group B under [condition]."
    6. Mechanistic: "Because [mechanism or process], [Variable A] will cause [Variable B]."
    7. Descriptive (Exploratory/Pattern-Oriented): "Population X exhibits pattern Y in context Z."

    If omitted, defaults to concise declarative sentences.
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
            "name": "HypothesisGenerator",
            "arguments": {
                "context": context,
                "domain": domain,
                "number_of_hypotheses": number_of_hypotheses,
                "hypothesis_format": hypothesis_format,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["HypothesisGenerator"]
