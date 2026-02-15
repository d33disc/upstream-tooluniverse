"""
ClinGenAR_lookup_allele

Look up variant by HGVS in ClinGen AR...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def ClinGenAR_lookup_allele(
    hgvs: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Look up variant by HGVS in ClinGen AR...
    """
    return get_shared_client().run_one_function(
        {
            "name": "ClinGenAR_lookup_allele",
            "arguments": {"hgvs": hgvs},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ClinGenAR_lookup_allele"]
