"""
OpenTriviaDB_get_questions

Get trivia questions from the Open Trivia Database, a free user-contributed trivia question datab...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OpenTriviaDB_get_questions(
    amount: Optional[int | Any] = None,
    category: Optional[int | Any] = None,
    difficulty: Optional[str | Any] = None,
    type_: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get trivia questions from the Open Trivia Database, a free user-contributed trivia question datab...

    Parameters
    ----------
    amount : int | Any
        Number of questions to retrieve (1-50, default: 10)
    category : int | Any
        Category ID. Options: 9=General Knowledge, 10=Books, 11=Film, 12=Music, 13=Mu...
    difficulty : str | Any
        Question difficulty: 'easy', 'medium', or 'hard'
    type_ : str | Any
        Question type: 'multiple' (multiple choice) or 'boolean' (true/false)
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
            "name": "OpenTriviaDB_get_questions",
            "arguments": {
                "amount": amount,
                "category": category,
                "difficulty": difficulty,
                "type": type_,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenTriviaDB_get_questions"]
