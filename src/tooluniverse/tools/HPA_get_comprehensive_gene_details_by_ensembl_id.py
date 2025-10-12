"""
HPA_get_comprehensive_gene_details_by_ensembl_id

Get detailed in-depth information from gene page using Ensembl Gene ID, including image URLs, antibody data, protein expression, and comprehensive information. This is the core tool for retrieving all images (tissue immunohistochemistry, subcellular immunofluorescence).
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


def HPA_get_comprehensive_gene_details_by_ensembl_id(
    ensembl_id: str,
    include_images: Optional[bool] = None,
    include_antibodies: Optional[bool] = None,
    include_expression: Optional[bool] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get detailed in-depth information from gene page using Ensembl Gene ID, including image URLs, antibody data, protein expression, and comprehensive information. This is the core tool for retrieving all images (tissue immunohistochemistry, subcellular immunofluorescence).

    Parameters
    ----------
    ensembl_id : str
        Ensembl Gene ID, e.g., 'ENSG00000064787' (BCAS1), 'ENSG00000141510' (TP53), etc. Usually obtained through HPA_search_genes_by_query tool.
    include_images : bool
        Whether to include image URL information (immunofluorescence, cell line images, etc.), defaults to true.
    include_antibodies : bool
        Whether to include detailed antibody information (validation status, Western blot data, etc.), defaults to true.
    include_expression : bool
        Whether to include detailed expression data (tissue specificity, subcellular localization, etc.), defaults to true.
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
            "name": "HPA_get_comprehensive_gene_details_by_ensembl_id",
            "arguments": {
                "ensembl_id": ensembl_id,
                "include_images": include_images,
                "include_antibodies": include_antibodies,
                "include_expression": include_expression,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["HPA_get_comprehensive_gene_details_by_ensembl_id"]
