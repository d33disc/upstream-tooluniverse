"""
embedding_database_create

Create a new embedding database from a collection of documents. Generates embeddings using OpenAI or Azure OpenAI models and stores them in a searchable database with FAISS vector index and SQLite metadata storage.
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


def embedding_database_create(
    database_name: str,
    documents: list[Any],
    action: Optional[str] = None,
    metadata: Optional[list[Any]] = None,
    model: Optional[str] = "text-embedding-3-small",
    description: Optional[str] = "",
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Create a new embedding database from a collection of documents. Generates embeddings using OpenAI or Azure OpenAI models and stores them in a searchable database with FAISS vector index and SQLite metadata storage.

    Parameters
    ----------
    action : str
        Action to create database from documents
    database_name : str
        Name for the new database (must be unique)
    documents : list[Any]
        List of document texts to embed and store
    metadata : list[Any]
        Optional metadata for each document (same length as documents)
    model : str
        OpenAI/Azure OpenAI embedding model to use
    description : str
        Optional description for the database
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
            "name": "embedding_database_create",
            "arguments": {
                "action": action,
                "database_name": database_name,
                "documents": documents,
                "metadata": metadata,
                "model": model,
                "description": description,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["embedding_database_create"]
