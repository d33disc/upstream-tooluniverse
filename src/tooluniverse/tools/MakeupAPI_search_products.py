"""
MakeupAPI_search_products

Search for cosmetics and makeup products by brand, type, category, tags, and price range using th...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def MakeupAPI_search_products(
    brand: Optional[str | Any] = None,
    product_type: Optional[str | Any] = None,
    product_category: Optional[str | Any] = None,
    product_tags: Optional[str | Any] = None,
    price_greater_than: Optional[float | Any] = None,
    price_less_than: Optional[float | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for cosmetics and makeup products by brand, type, category, tags, and price range using th...

    Parameters
    ----------
    brand : str | Any
        Filter by brand name (lowercase). Options include: 'maybelline', 'covergirl',...
    product_type : str | Any
        Filter by product type. Options: 'blush', 'bronzer', 'eyebrow', 'eyeliner', '...
    product_category : str | Any
        Filter by sub-category. Options include: 'powder', 'cream', 'liquid', 'pencil...
    product_tags : str | Any
        Filter by tag (comma-separated). Options: 'vegan', 'organic', 'natural', 'can...
    price_greater_than : float | Any
        Minimum price filter in USD
    price_less_than : float | Any
        Maximum price filter in USD
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
    # Handle mutable defaults to avoid B006 linting error

    return get_shared_client().run_one_function(
        {
            "name": "MakeupAPI_search_products",
            "arguments": {
                "brand": brand,
                "product_type": product_type,
                "product_category": product_category,
                "product_tags": product_tags,
                "price_greater_than": price_greater_than,
                "price_less_than": price_less_than,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["MakeupAPI_search_products"]
