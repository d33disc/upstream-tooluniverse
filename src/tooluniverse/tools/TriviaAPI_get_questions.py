"""
TriviaAPI_get_questions

Get trivia questions from The Trivia API (the-trivia-api.com). Returns questions with correct ans...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def TriviaAPI_get_questions(
    categories: Optional[str | Any] = None,
    difficulty: Optional[str | Any] = None,
    limit: Optional[int | Any] = None,
    types: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get trivia questions from The Trivia API (the-trivia-api.com). Returns questions with correct ans...

    Parameters
    ----------
    categories : str | Any
        Comma-separated categories. Values: 'science', 'history', 'geography', 'sport...
    difficulty : str | Any
        Question difficulty. Values: 'easy', 'medium', 'hard'. Default: all difficulties
    limit : int | Any
        Number of questions to return (1-50). Default: 5
    types : str | Any
        Question type. Values: 'text_choice' (multiple choice). Default: text_choice
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
    # Handle mutable defaults to avoid B006 linting error

    return get_shared_client().run_one_function(
        {
            "name": "TriviaAPI_get_questions",
            "arguments": {
                "categories": categories,
                "difficulty": difficulty,
                "limit": limit,
                "types": types,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["TriviaAPI_get_questions"]
