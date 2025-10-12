"""
humanbase_ppi_analysis

Retrieve tissue-specific protein-protein interactions and biological processes from HumanBase. Returns a NetworkX graph of tissue specific protein-protein interactions and a list of associated biological processes involeed by the given genes from Gene Ontology.
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


def humanbase_ppi_analysis(
    gene_list: list[Any],
    tissue: Optional[str] = "brain",
    max_node: Optional[int] = 10,
    interaction: Optional[str] = None,
    string_mode: Optional[bool] = True,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve tissue-specific protein-protein interactions and biological processes from HumanBase. Returns a NetworkX graph of tissue specific protein-protein interactions and a list of associated biological processes involeed by the given genes from Gene Ontology.

    Parameters
    ----------
    gene_list : list[Any]
        List of gene names or symbols to analyze for protein-protein interactions. The gene name should be the official gene symbol, not the synonym.
    tissue : str
        Tissue type for tissue-specific interactions. Examples: 'brain', 'heart', 'liver', 'kidney', etc.
    max_node : int
        Maximum number of nodes to retrieve in the interaction network. Warning: the more nodes, the more time it takes to retrieve the data. Default is 10 (~30 seconds).
    interaction : str
        Specific interaction type to filter by. Available types: 'co-expression', 'interaction', 'tf-binding', 'gsea-microrna-targets', 'gsea-perturbations'. If not specified, all types will be included.
    string_mode : bool
        Whether to return the result in string mode. If True, the result will be a string of the network graph and the biological processes. If False, the result will be a NetworkX graph and a list of biological processes.
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
            "name": "humanbase_ppi_analysis",
            "arguments": {
                "gene_list": gene_list,
                "tissue": tissue,
                "max_node": max_node,
                "interaction": interaction,
                "string_mode": string_mode,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["humanbase_ppi_analysis"]
