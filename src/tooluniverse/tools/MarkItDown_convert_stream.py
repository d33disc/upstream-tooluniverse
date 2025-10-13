"""
MarkItDown_convert_stream

Convert file content from a stream (bytes) to Markdown using Microsoft's MarkItDown library. Usef...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def MarkItDown_convert_stream(
    file_content: str,
    file_extension: str,
    enable_plugins: Optional[bool] = False,
    docintel_endpoint: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Convert file content from a stream (bytes) to Markdown using Microsoft's MarkItDown library. Usef...

    Parameters
    ----------
    file_content : str
        Base64 encoded file content to convert
    file_extension : str
        File extension to determine conversion method (e.g., '.pdf', '.docx', '.pptx')
    enable_plugins : bool
        Whether to enable 3rd-party plugins for enhanced conversion
    docintel_endpoint : str
        Optional Azure Document Intelligence endpoint for enhanced PDF processing
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
    # Handle mutable defaults to avoid B006 linting error

    return get_shared_client().run_one_function(
        {
            "name": "MarkItDown_convert_stream",
            "arguments": {
                "file_content": file_content,
                "file_extension": file_extension,
                "enable_plugins": enable_plugins,
                "docintel_endpoint": docintel_endpoint,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["MarkItDown_convert_stream"]
