"""
alphafold_get_annotations

Retrieve AlphaFold variant annotations (e.g., missense mutations) for a given UniProt accession (e.g., 'P69905'). Input must be a UniProt accession, entry name, or CRC64 checksum, along with an annotation type (currently only 'MUTAGEN'). Use this tool to explore predicted pathogenicity or functional effects of substitutions. If you only have a protein/gene name, resolve it with `uniprot_search`. For experimentally curated variants, use `UniProt_get_disease_variants_by_accession`. To view the full 3D structure, call `alphafold_get_prediction`; for overall model metadata, use `alphafold_get_summary`.
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


def alphafold_get_annotations(
    qualifier: str,
    type: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Retrieve AlphaFold variant annotations (e.g., missense mutations) for a given UniProt accession (e.g., 'P69905'). Input must be a UniProt accession, entry name, or CRC64 checksum, along with an annotation type (currently only 'MUTAGEN'). Use this tool to explore predicted pathogenicity or functional effects of substitutions. If you only have a protein/gene name, resolve it with `uniprot_search`. For experimentally curated variants, use `UniProt_get_disease_variants_by_accession`. To view the full 3D structure, call `alphafold_get_prediction`; for overall model metadata, use `alphafold_get_summary`.

    Parameters
    ----------
    qualifier : str
        Protein identifier: UniProt accession, entry name, or CRC64 checksum.
    type : str
        Annotation type (currently only 'MUTAGEN' is supported).
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
            "name": "alphafold_get_annotations",
            "arguments": {"qualifier": qualifier, "type": type},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["alphafold_get_annotations"]
