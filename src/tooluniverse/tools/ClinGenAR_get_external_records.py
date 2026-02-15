"""
ClinGenAR_get_external_records

Get external DB records for allele...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def ClinGenAR_get_external_records(
    allele_id: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get external DB records for allele...
    """
    return get_shared_client().run_one_function(
        {
            "name": "ClinGenAR_get_external_records",
            "arguments": {"allele_id": allele_id},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ClinGenAR_get_external_records"]
