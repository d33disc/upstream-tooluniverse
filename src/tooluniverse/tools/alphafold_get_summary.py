"""
alphafold_get_summary

Retrieve summary details of AlphaFold 3D models for a given protein. Input must be a UniProt accession, entry name, or CRC64 checksum. Returns lightweight information such as sequence length, coverage, confidence scores, experimental method, resolution, oligomeric state, and structural entities. If you only know the protein/gene name, first use `uniprot_search` to find the accession. For full residue-level 3D predictions with downloadable coordinates, call `alphafold_get_prediction`. For curated variants, see `UniProt_get_disease_variants_by_accession`; for predicted mutation effects, use `alphafold_get_annotations`.
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


def alphafold_get_summary(
    qualifier: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Retrieve summary details of AlphaFold 3D models for a given protein. Input must be a UniProt accession, entry name, or CRC64 checksum. Returns lightweight information such as sequence length, coverage, confidence scores, experimental method, resolution, oligomeric state, and structural entities. If you only know the protein/gene name, first use `uniprot_search` to find the accession. For full residue-level 3D predictions with downloadable coordinates, call `alphafold_get_prediction`. For curated variants, see `UniProt_get_disease_variants_by_accession`; for predicted mutation effects, use `alphafold_get_annotations`.

    Parameters
    ----------
    qualifier : str
        Protein identifier: UniProt accession, entry name, or CRC64 checksum.
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
        {"name": "alphafold_get_summary", "arguments": {"qualifier": qualifier}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["alphafold_get_summary"]
