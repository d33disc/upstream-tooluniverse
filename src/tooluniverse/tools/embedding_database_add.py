"""
embedding_database_add

Add new documents to an existing embedding database. Generates embeddings for new documents using the same model as the original database and appends them to the existing FAISS index.
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


def embedding_database_add(
    database_name: str,
    documents: list[Any],
    action: Optional[str] = None,
    metadata: Optional[list[Any]] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Add new documents to an existing embedding database. Generates embeddings for new documents using the same model as the original database and appends them to the existing FAISS index.

    Parameters
    ----------
    action : str
        Action to add documents to existing database
    database_name : str
        Name of the existing database to add documents to
    documents : list[Any]
        List of new document texts to embed and add
    metadata : list[Any]
        Optional metadata for each new document (same length as documents)
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
    if metadata is None:
        metadata = []

    return _get_client().run_one_function(
        {
            "name": "embedding_database_add",
            "arguments": {
                "action": action,
                "database_name": database_name,
                "documents": documents,
                "metadata": metadata,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["embedding_database_add"]
