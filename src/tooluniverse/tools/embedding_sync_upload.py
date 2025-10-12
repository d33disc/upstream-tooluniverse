"""
embedding_sync_upload

Upload a local embedding database to HuggingFace Hub for sharing and collaboration. Creates a dat...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def embedding_sync_upload(
    database_name: str,
    repository: str,
    action: Optional[str] = None,
    description: Optional[str] = "",
    private: Optional[bool] = False,
    commit_message: Optional[str] = "Upload embedding database",
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Upload a local embedding database to HuggingFace Hub for sharing and collaboration. Creates a dat...

    Parameters
    ----------
    action : str
        Action to upload database to HuggingFace
    database_name : str
        Name of the local database to upload
    repository : str
        HuggingFace repository name (format: username/repo-name)
    description : str
        Description for the HuggingFace dataset
    private : bool
        Whether to create a private repository
    commit_message : str
        Commit message for the upload
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
            "name": "embedding_sync_upload",
            "arguments": {
                "action": action,
                "database_name": database_name,
                "repository": repository,
                "description": description,
                "private": private,
                "commit_message": commit_message,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["embedding_sync_upload"]
