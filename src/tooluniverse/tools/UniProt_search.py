"""
UniProt_search

Search UniProtKB database using flexible query syntax.
Supports gene names (e.g., 'gene:TP53'), protein names,
organism filters, and complex queries.
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def UniProt_search(
    query: str,
    organism: Optional[str] = None,
    limit: Optional[int] = None,
    fields: Optional[list[Any]] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search UniProtKB database with flexible query syntax.

    Search UniProtKB and return protein entries. Supports field searches,
    ranges, wildcards, boolean operators, and parentheses for grouping.

    Parameters
    ----------
    query : str
        Search query. Examples:
        - Simple: 'MEIOB', 'insulin'
        - Field: 'gene:TP53', 'organism_id:9606', 'reviewed:true'
        - Range: 'length:[100 TO 500]', 'mass:[20000 TO 50000]'
        - Wildcard: 'gene:MEIOB*'
        - Boolean: 'gene:TP53 AND organism_id:9606'
        - Grouped: '(organism_id:9606 OR organism_id:10090) AND
          gene:TP53'
    organism : str, optional
        Organism filter. Use 'human', 'mouse', 'rat', 'yeast' or
        taxonomy ID like '9606'. Combined with query using AND.
    limit : int, optional
        Maximum results to return (default: 25, max: 500).
        Accepts string or integer.
    fields : list[str], optional
        Field names to return. When specified, returns raw API response.
        Common: accession, id, gene_names, gene_primary, protein_name,
        organism_name, organism_id, length, mass, sequence, reviewed,
        cc_function.
        Default: formatted response with accession, id, protein_name,
        gene_names, organism, length.
    min_length : int, optional
        Minimum sequence length. Converts to 'length:[min TO *]'.
    max_length : int, optional
        Maximum sequence length. Converts to 'length:[* TO max]'.
    stream_callback : callable, optional
        Callback for streaming output
    use_cache : bool, default False
        Enable caching
    validate : bool, default True
        Validate parameters

    Returns
    -------
    dict
        Search results with total_results, returned count, and results
        list

    Examples
    --------
    >>> UniProt_search("gene:TP53", organism="human", limit=5)
    >>> UniProt_search("insulin", fields=['accession', 'length'])
    >>> UniProt_search("gene:MEIOB", min_length=400, max_length=500)
    """
    # Handle mutable defaults to avoid B006 linting error

    return get_shared_client().run_one_function(
        {
            "name": "UniProt_search",
            "arguments": {
                "query": query,
                "organism": organism,
                "limit": limit,
                "fields": fields,
                "min_length": min_length,
                "max_length": max_length,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["UniProt_search"]
