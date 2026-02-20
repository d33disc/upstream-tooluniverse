"""
Datamuse_find_related_words

Find words related by meaning, sound, or spelling using the Datamuse word-finding API. Supports f...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Datamuse_find_related_words(
    ml: Optional[str | Any] = None,
    sl: Optional[str | Any] = None,
    sp: Optional[str | Any] = None,
    rel_rhy: Optional[str | Any] = None,
    rel_syn: Optional[str | Any] = None,
    rel_ant: Optional[str | Any] = None,
    rel_trg: Optional[str | Any] = None,
    topics: Optional[str | Any] = None,
    max: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Find words related by meaning, sound, or spelling using the Datamuse word-finding API. Supports f...

    Parameters
    ----------
    ml : str | Any
        Words with similar meaning to this word/phrase. Examples: 'ringing in the ear...
    sl : str | Any
        Words that sound like this word. Examples: 'jirraf', 'elefant'
    sp : str | Any
        Words spelled like this pattern (* for wildcard). Examples: 'b*k', 't*tion'
    rel_rhy : str | Any
        Words that rhyme with this word. Examples: 'spade', 'cat'
    rel_syn : str | Any
        Synonyms of this word (WordNet). Examples: 'happy', 'fast'
    rel_ant : str | Any
        Antonyms of this word. Examples: 'hot', 'good'
    rel_trg : str | Any
        Words commonly associated with or triggered by this word. Examples: 'cow', 'd...
    topics : str | Any
        Hint about the topic/domain. Examples: 'finance', 'biology'
    max : int | Any
        Maximum number of results (1-1000). Default: 100
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
            "name": "Datamuse_find_related_words",
            "arguments": {
                "ml": ml,
                "sl": sl,
                "sp": sp,
                "rel_rhy": rel_rhy,
                "rel_syn": rel_syn,
                "rel_ant": rel_ant,
                "rel_trg": rel_trg,
                "topics": topics,
                "max": max,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Datamuse_find_related_words"]
