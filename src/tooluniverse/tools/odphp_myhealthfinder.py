"""
odphp_myhealthfinder

This tool provides personalized preventive-care recommendations and it is helpful for different ages, sexes, pregnancy status, gives age/sex/pregnancy. It retrieves metadata, plain-language sections, and dataset links to the full article (AccessibleVersion links). If the user wants the full text of a recommendation, the `odphp_outlink_fetch` tool is helpful.
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


def odphp_myhealthfinder(
    lang: Optional[str] = None,
    age: Optional[int] = None,
    sex: Optional[str] = None,
    pregnant: Optional[str] = None,
    strip_html: Optional[bool] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    This tool provides personalized preventive-care recommendations and it is helpful for different ages, sexes, pregnancy status, gives age/sex/pregnancy. It retrieves metadata, plain-language sections, and dataset links to the full article (AccessibleVersion links). If the user wants the full text of a recommendation, the `odphp_outlink_fetch` tool is helpful.

    Parameters
    ----------
    lang : str
        Language code (en or es)
    age : int
        Age in years (0–120)
    sex : str
        Male or Female
    pregnant : str
        "Yes" or "No"
    strip_html : bool
        If true, also return PlainSections[] with HTML removed for each topic
    stream_callback : Callable, optional
        Callback for streaming output
    use_cache : bool, default False
        Enable caching
    validate : bool, default True
        Validate parameters

    Returns
    -------
    dict[str, Any]
    """
    return _get_client().run_one_function(
        {
            "name": "odphp_myhealthfinder",
            "arguments": {
                "lang": lang,
                "age": age,
                "sex": sex,
                "pregnant": pregnant,
                "strip_html": strip_html,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["odphp_myhealthfinder"]
