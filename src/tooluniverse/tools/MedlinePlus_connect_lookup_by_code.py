"""
MedlinePlus_connect_lookup_by_code

Look up corresponding MedlinePlus page information through MedlinePlus Connect Web Service using clinical/drug/test codes (such as ICD-10 CM, RXCUI, LOINC, etc.), supports JSON or XML format return.
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


def MedlinePlus_connect_lookup_by_code(
    cs: str,
    c: str,
    dn: Optional[str] = "",
    language: Optional[str] = "en",
    format: Optional[str] = "json",
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Look up corresponding MedlinePlus page information through MedlinePlus Connect Web Service using clinical/drug/test codes (such as ICD-10 CM, RXCUI, LOINC, etc.), supports JSON or XML format return.

    Parameters
    ----------
    cs : str
        Code system OID, e.g., ICD-10 CM=2.16.840.1.113883.6.90, RXCUI=2.16.840.1.113883.6.88, LOINC=2.16.840.1.113883.6.1, etc.
    c : str
        Specific code value to query, e.g., "E11.9" (ICD-10 CM) or "637188" (RXCUI).
    dn : str
        Optional, descriptive name (English) corresponding to the code, for drugs can fill in "Chantix 0.5 MG Oral Tablet", can improve matching accuracy.
    language : str
        Return information language, "en" for English, "es" for Spanish, default "en".
    format : str
        Return format, options "json" or "xml", default "json".
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
            "name": "MedlinePlus_connect_lookup_by_code",
            "arguments": {
                "cs": cs,
                "c": c,
                "dn": dn,
                "language": language,
                "format": format,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["MedlinePlus_connect_lookup_by_code"]
