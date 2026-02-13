"""
STRING_map_identifiers

Map protein identifiers to STRING (Search Tool for Retrieval of Interacting Genes/Proteins) database IDs. Essential first step before using other STRING tools - converts your protein names (gene symbols, UniProt IDs, Ensembl IDs) to STRING's internal identifiers. STRING database contains 14M+ proteins from 5,000+ organisms with functional association networks. No API key required (public API with rate limits). Use for: preparing protein lists for network analysis, converting between identifier types, validating protein names exist in STRING, batch identifier conversion.
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def STRING_map_identifiers(
    protein_ids: list[str],
    species: Optional[int] = 9606,
    limit: Optional[int] = 1,
    echo_query: Optional[int] = 1,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> list[Any]:
    """
    Map protein identifiers to STRING (Search Tool for Retrieval of Interacting Genes/Proteins) database IDs.

    Essential first step before using other STRING tools - converts your protein names to STRING's internal
    identifiers. No API key required.

    Parameters
    ----------
    protein_ids : list[str]
        List of protein identifiers in any format (gene symbols like 'TP53', UniProt IDs like 'P04637',
        Ensembl IDs like 'ENSP00000269305'). Accepts mixed formats. Example: ['TP53', 'MDM2', 'P53_HUMAN'].
    species : int
        NCBI taxonomy ID specifying organism. Common values: 9606 (Homo sapiens/human), 10090 (Mus musculus/mouse),
        10116 (Rattus norvegicus/rat), 7227 (Drosophila melanogaster). Default 9606 (human).
    limit : int
        Maximum matches per identifier. 1 (default, most common match), 2-5 (include close matches),
        higher (get all possibilities). Recommend keeping default 1 unless identifier is ambiguous.
    echo_query : int
        Include query identifier in response (1=yes, 0=no, default: 1)
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
    # Handle mutable defaults to avoid B006 linting error

    return get_shared_client().run_one_function(
        {
            "name": "STRING_map_identifiers",
            "arguments": {
                "protein_ids": protein_ids,
                "species": species,
                "limit": limit,
                "echo_query": echo_query,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["STRING_map_identifiers"]
