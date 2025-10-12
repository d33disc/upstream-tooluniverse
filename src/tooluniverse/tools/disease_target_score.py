"""
disease_target_score

Extract disease-target association scores from a specific data source using GraphQL API. This tool retrieves all targets associated with a disease and their scores from a specified datasource (e.g., chembl, eva, cancer_gene_census, etc.).
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


def disease_target_score(
    efoId: str,
    datasourceId: str,
    pageSize: Optional[int] = 100,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Extract disease-target association scores from a specific data source using GraphQL API. This tool retrieves all targets associated with a disease and their scores from a specified datasource (e.g., chembl, eva, cancer_gene_census, etc.).

    Parameters
    ----------
    efoId : str
        The EFO (Experimental Factor Ontology) ID of the disease, e.g., 'EFO_0000339' for chronic myelogenous leukemia
    datasourceId : str
        The datasource ID to extract scores from. Available options: 'chembl', 'eva', 'eva_somatic', 'cancer_gene_census', 'cancer_biomarkers', 'europepmc', 'expression_atlas', 'genomics_england', 'impc', 'reactome', 'uniprot_literature', 'uniprot_variants'
    pageSize : int
        Number of results per page (default: 100, max: 100)
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
            "name": "disease_target_score",
            "arguments": {
                "efoId": efoId,
                "datasourceId": datasourceId,
                "pageSize": pageSize,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["disease_target_score"]
