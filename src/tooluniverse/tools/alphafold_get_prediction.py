"""
alphafold_get_prediction

Retrieve full AlphaFold 3D structure predictions for a given protein. Input must be a UniProt accession (e.g., 'P69905'), UniProt entry name (e.g., 'HBA_HUMAN'), or CRC64 checksum. Returns residue-level metadata including sequence, per-residue confidence scores (pLDDT), and structure download links (PDB, CIF, PAE). If you do not know the accession, first call `uniprot_search` to resolve it from a protein/gene name, or `UniProt_get_entry_by_accession` if you already have the accession and want UniProt details. For a quick overview, use `alphafold_get_summary`. For mutation/variant impact, see `alphafold_get_annotations.
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


def alphafold_get_prediction(
    qualifier: str,
    sequence_checksum: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> list[Any]:
    """
    Retrieve full AlphaFold 3D structure predictions for a given protein. Input must be a UniProt accession (e.g., 'P69905'), UniProt entry name (e.g., 'HBA_HUMAN'), or CRC64 checksum. Returns residue-level metadata including sequence, per-residue confidence scores (pLDDT), and structure download links (PDB, CIF, PAE). If you do not know the accession, first call `uniprot_search` to resolve it from a protein/gene name, or `UniProt_get_entry_by_accession` if you already have the accession and want UniProt details. For a quick overview, use `alphafold_get_summary`. For mutation/variant impact, see `alphafold_get_annotations.

    Parameters
    ----------
    qualifier : str
        Protein identifier: UniProt accession (e.g., 'P69905'), entry name (e.g., 'HBA_HUMAN'), or CRC64 checksum.
    sequence_checksum : str
        Optional CRC64 checksum of the UniProt sequence.
    stream_callback : Callable, optional
        Callback for streaming output
    use_cache : bool, default False
        Enable caching
    validate : bool, default True
        Validate parameters

    Returns
    -------
    list[Any]
    """
    return _get_client().run_one_function(
        {
            "name": "alphafold_get_prediction",
            "arguments": {
                "qualifier": qualifier,
                "sequence_checksum": sequence_checksum,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["alphafold_get_prediction"]
