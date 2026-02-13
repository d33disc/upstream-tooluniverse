"""
STRING_get_interaction_partners

Find direct interaction partners for a single protein from STRING (Search Tool for Retrieval of Interacting Genes/Proteins). Simpler alternative to STRING_get_network when analyzing one protein - returns ranked list of interacting partners with confidence scores (0-1.0). Use this for focused analysis of single proteins; use STRING_get_network for complete network between multiple proteins. No API key required. Returns: partner protein IDs, confidence scores, evidence types, partner annotations. Use for: discovering interacting partners of a single protein, identifying potential drug targets, finding binding partners, exploring single protein biology, quick partner lookup.
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def STRING_get_interaction_partners(
    protein_ids: list[str],
    species: Optional[int] = 9606,
    confidence_score: Optional[float] = 0.4,
    limit: Optional[int] = 20,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> list[Any]:
    """
    Get direct interaction partners for a protein with confidence scores from STRING database. Return...

    Parameters
    ----------
    protein_ids : list[str]
        List of protein identifiers (UniProt IDs, gene names, Ensembl IDs)
    species : int
        NCBI taxonomy ID (default: 9606 for human, 10090 for mouse)
    confidence_score : float
        Minimum confidence score (0-1, default: 0.4 for medium confidence)
    limit : int
        Maximum number of interaction partners to return (default: 20)
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
            "name": "STRING_get_interaction_partners",
            "arguments": {
                "protein_ids": protein_ids,
                "species": species,
                "confidence_score": confidence_score,
                "limit": limit,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["STRING_get_interaction_partners"]
