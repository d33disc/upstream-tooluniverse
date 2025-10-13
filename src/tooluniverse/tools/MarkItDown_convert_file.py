"""
MarkItDown_convert_file

Convert various file formats (PDF, Word, PowerPoint, Excel, images, audio, HTML, etc.) to Markdow...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def MarkItDown_convert_file(
    file_path: str,
    output_path: Optional[str] = None,
    enable_plugins: Optional[bool] = False,
    docintel_endpoint: Optional[str] = None,
    llm_client: Optional[str] = None,
    llm_model: Optional[str] = None,
    llm_prompt: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Convert various file formats (PDF, Word, PowerPoint, Excel, images, audio, HTML, etc.) to Markdow...

    Parameters
    ----------
    file_path : str
        Path to the file to convert to Markdown
    output_path : str
        Optional output path for the Markdown file. If not provided, returns the cont...
    enable_plugins : bool
        Whether to enable 3rd-party plugins for enhanced conversion
    docintel_endpoint : str
        Optional Azure Document Intelligence endpoint for enhanced PDF processing
    llm_client : str
        Optional LLM client configuration for image descriptions (JSON string)
    llm_model : str
        LLM model to use for image descriptions (e.g., 'gpt-4o')
    llm_prompt : str
        Custom prompt for LLM-based image descriptions
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
            "name": "MarkItDown_convert_file",
            "arguments": {
                "file_path": file_path,
                "output_path": output_path,
                "enable_plugins": enable_plugins,
                "docintel_endpoint": docintel_endpoint,
                "llm_client": llm_client,
                "llm_model": llm_model,
                "llm_prompt": llm_prompt,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["MarkItDown_convert_file"]
