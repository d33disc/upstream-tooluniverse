# Configuration file for the Sphinx documentation builder with Furo theme.
# Modern, clean, and responsive documentation theme configuration

import os
import sys
import re

sys.path.insert(0, os.path.abspath("../src"))

# -- Project information -----------------------------------------------------
project = "ToolUniverse"
copyright = "2025, Shanghua Gao"
author = "Shanghua Gao"
release = "1.0.0"

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.mathjax",
    "sphinx.ext.githubpages",
    "sphinx.ext.autosummary",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.doctest",
    "sphinx.ext.extlinks",
    "sphinx.ext.linkcode",
    "sphinx_autodoc_typehints",
    "myst_parser",
    "sphinx_copybutton",
    "sphinx_tabs.tabs",
    "sphinx_design",
    "notfound.extension",
]

# -- Toctree configuration ---------------------------------------------------
# Include hidden toctree entries in the sidebar navigation
toc_includehidden = True

# -- Sidebar configuration ---------------------------------------------------
# Use Furo's default sidebar configuration for proper navigation
html_sidebars = {
    "**": [
        "sidebar/brand.html",
        "sidebar/search.html",
        "sidebar/scroll-start.html",
        "sidebar/navigation.html",
        "sidebar/scroll-end.html",
    ]
}

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output with Furo theme --------------------------------
html_theme = "furo"
html_static_path = ["_static"]

# -- Enhanced Furo theme configuration ---------------------------------------
html_theme_options = {
    # Color scheme
    "light_css_variables": {
        "color-brand-primary": "#2980B9",
        "color-brand-content": "#2980B9",
        "color-admonition-background": "#f8f9fa",
        "color-api-background": "#f8f9fa",
        "color-api-background-hover": "#e9ecef",
        "color-sidebar-background": "#ffffff",
        "color-sidebar-background-border": "#eeeeee",
        # Typography
        "font-stack": "system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif, Apple Color Emoji, Segoe UI Emoji",
        "font-stack--monospace": "Consolas, Monaco, 'Andale Mono', 'Ubuntu Mono', monospace",
        # Spacing and sizes
        "sidebar-caption-space-above": "2rem",
        "api-font-size": "var(--font-size--small)",
        "admonition-font-size": "0.9rem",
        # Links
        "color-link": "#2980B9",
        "color-link--hover": "#1f5f8b",
    },
    "dark_css_variables": {
        "color-brand-primary": "#3498DB",
        "color-brand-content": "#3498DB",
        "color-admonition-background": "#1e1e1e",
        "color-api-background": "#1e1e1e",
        "color-api-background-hover": "#2d2d2d",
        "color-sidebar-background": "#131416",
        "color-sidebar-background-border": "#303335",
        # Dark mode typography
        "color-foreground-primary": "#efefef",
        "color-foreground-secondary": "#c9c9c9",
        "color-foreground-muted": "#81868d",
        # Dark mode links
        "color-link": "#3498DB",
        "color-link--hover": "#5dade2",
    },
    # Navigation and layout
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
    "top_of_page_button": None,
    # Code and content
    "source_repository": "https://github.com/mims-harvard/ToolUniverse",
    "source_branch": "main",
    "source_directory": "docs/",
    # Footer
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/mims-harvard/ToolUniverse",
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,
            "class": "",
        },
        {
            "name": "Slack",
            "url": "https://aiscientist.tools/#:~:text=Join%20Slack%20Community",
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path d="M3.362 10.11c0 .926-.756 1.682-1.681 1.682S0 11.036 0 10.111C0 9.186.756 8.43 1.681 8.43h1.681v1.68zm.846 0c0-.924.756-1.68 1.681-1.68s1.681.756 1.681 1.68v4.21c0 .924-.756 1.68-1.681 1.68s-1.681-.756-1.681-1.68v-4.21zm6.725 1.682c-.926 0-1.682-.756-1.682-1.681s.756-1.681 1.682-1.681h1.681v1.681c0 .925-.756 1.681-1.681 1.681zm-1.681-1.682c0-.924.756-1.68 1.681-1.68s1.681.756 1.681 1.68v1.681H9.431v-1.68zm1.681-6.725c.926 0 1.681-.756 1.681-1.681S11.037 0 10.112 0H8.43v1.681c0 .926.756 1.681 1.681 1.681zm-1.681 0c0 .924-.756 1.68-1.681 1.68S5.069 2.405 5.069 1.48V0H3.388v1.48c0 .924.756 1.68 1.681 1.68zm1.681 0c.926 0 1.681.756 1.681 1.681s-.756 1.681-1.681 1.681H8.43V1.681c0-.925.756-1.681 1.681-1.681zM5.069 1.681c0-.925.756-1.681 1.681-1.681s1.681.756 1.681 1.681v1.681H5.069V1.681zm-1.681 6.725c-.926 0-1.681.756-1.681 1.681s.756 1.681 1.681 1.681h1.681V9.431c0-.925-.756-1.681-1.681-1.681zm0 .846c.924 0 1.68.756 1.68 1.681s-.756 1.681-1.68 1.681H1.681c-.925 0-1.681-.756-1.681-1.681s.756-1.681 1.681-1.681h1.681zm6.725-1.681c0 .926-.756 1.682-1.681 1.682s-1.681-.756-1.681-1.682V5.069h1.681c.925 0 1.681.756 1.681 1.681z"/>
                </svg>
            """,
            "class": "",
        },
    ],
}

# -- Logo and branding -------------------------------------------------------
html_title = f"{project} Documentation"
html_logo = "_static/logo.png" if os.path.exists("_static/logo.png") else None
html_favicon = "_static/logo_transparent.png" if os.path.exists("_static/logo_transparent.png") else None

# -- Custom CSS for enhanced styling ----------------------------------------
html_css_files = [
    "furo_custom.css",
]

# -- Extension configuration -------------------------------------------------

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

# Autodoc settings - Enhanced to include all functions and classes
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "special-members": "__init__,__call__,__str__,__repr__",
    "private-members": False,
    "exclude-members": "__weakref__",
    "member-order": "bysource",
    "imported-members": True,
    "show-source": True,
}

# Render type hints in the description for better readability
autodoc_typehints = "description"
typehints_defaults = "comma"
typehints_fully_qualified = False

# Avoid importing heavy optional dependencies during docs build
autodoc_mock_imports = [
    "torch",
    "torchvision",
    "torchaudio",
    "chemprop",
    "faiss",
    "faiss_cpu",
    "faiss-gpu",
    "playwright",
    "pygraphviz",
    "graphviz",
    "pydot",
    "matplotlib",
    "scipy",
]

# MyST parser settings
myst_enable_extensions = [
    "deflist",
    "tasklist",
    "dollarmath",
    "amsmath",
    "colon_fence",
    "attrs_inline",
    "attrs_block",
    "linkify",
]

# Todo extension settings
todo_include_todos = True

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "requests": ("https://docs.python-requests.org/en/latest/", None),
}

# Sphinx-copybutton settings
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True
copybutton_line_continuation_character = "\\"
copybutton_here_doc_delimiter = "EOF"

# Sphinx-tabs settings
sphinx_tabs_valid_builders = ["linkcheck"]
sphinx_tabs_disable_tab_closing = False

# Autosummary settings for comprehensive API documentation
autosummary_generate = True
autosummary_imported_members = True
autosummary_ignore_module_all = False

# Autosectionlabel settings
autosectionlabel_prefix_document = True
autosectionlabel_maxdepth = 3

# NotFound extension settings
notfound_context = {
    "title": "Page Not Found",
    "body": """
    <h2>🔍 Oops! Page not found.</h2>
    <p>The page you're looking for doesn't exist. Here are some helpful links:</p>
    <div class="admonition tip">
        <p class="admonition-title">Quick Navigation</p>
        <ul>
            <li><a href="index.html">🏠 Home</a></li>
            <li><a href="quickstart.html">🚀 Quick Start</a></li>
            <li><a href="guide/index.html">📖 User Guide</a></li>
            <li><a href="help/index.html">❓ Help</a></li>
        </ul>
    </div>
    """,
}

# Source file suffixes
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# Master document
master_doc = "index"

# GitHub Pages configuration
html_baseurl = "https://zitniklab.hms.harvard.edu/ToolUniverse/"
html_extra_path = []

# Enhanced HTML options for modern look
html_use_smartypants = False
html_show_sourcelink = True
html_show_sphinx = False  # Hide "Made with Sphinx" for cleaner footer
html_copy_source = False
html_show_copyright = True

# Language and search
language = "en"
html_search_language = "en"

# Better source code highlighting
pygments_style = "default"
pygments_dark_style = "monokai"  # Dark mode syntax highlighting

# Enhanced navigation
html_use_index = True
html_split_index = False
html_domain_indices = True

# Modern meta tags for better SEO and social sharing
html_meta = {
    "description": "ToolUniverse: A comprehensive scientific AI tool collection for drug discovery, literature analysis, and research workflows.",
    "keywords": "AI tools, scientific research, drug discovery, bioinformatics, API integration",
    "author": "Shanghua Gao",
    "viewport": "width=device-width, initial-scale=1.0",
    "og:title": "ToolUniverse Documentation",
    "og:description": "Comprehensive scientific AI tool collection for researchers and developers.",
    "og:type": "website",
    "twitter:card": "summary_large_image",
}

# -- Warning suppression -----------------------------------------------------
# Suppress warnings for external libraries (Flask, etc.)
suppress_warnings = [
    "ref.doc",  # Suppress unknown document warnings
    "ref.ref",  # Suppress undefined label warnings
]

# -- Intersphinx mapping for external libraries -----------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "flask": ("https://flask.palletsprojects.com/", None),
}

# -- Doctest configuration --------------------------------------------------
doctest_test_doctest_blocks = 'default'
doctest_global_setup = '''
import sys
import os
sys.path.insert(0, os.path.abspath('../src'))
'''
doctest_global_cleanup = '''
# Cleanup code if needed
'''

# -- Extlinks configuration --------------------------------------------------
extlinks = {
    'issue': ('https://github.com/mims-harvard/ToolUniverse/issues/%s', 'issue #%s'),
    'pr': ('https://github.com/mims-harvard/ToolUniverse/pull/%s', 'PR #%s'),
    'commit': ('https://github.com/mims-harvard/ToolUniverse/commit/%s', 'commit %s'),
    'github': ('https://github.com/mims-harvard/ToolUniverse/%s', '%s'),
}

# -- Linkcode configuration --------------------------------------------------


def linkcode_resolve(domain, info):
    """Resolve links to source code."""
    if domain != 'py':
        return None
    
    filename = info['module'].replace('.', '/')
    
    # Handle different module patterns
    if filename.startswith('tooluniverse/'):
        # Remove the tooluniverse/ prefix for GitHub links
        filename = filename[12:]  # Remove 'tooluniverse/'
        return (f"https://github.com/mims-harvard/ToolUniverse/blob/"
                f"main/src/tooluniverse/{filename}.py")
    else:
        return (f"https://github.com/mims-harvard/ToolUniverse/blob/"
                f"main/src/tooluniverse/{filename}.py")



# Custom setup function for additional enhancements


def setup(app):
    """Custom Sphinx setup function for enhanced functionality."""
    # Add custom CSS
    app.add_css_file("furo_custom.css")

    # Add analytics if needed
    # app.add_js_file('analytics.js')

    # Normalize Markdown-style constructs in docstrings to valid reStructuredText
    def _normalize_markdown_in_docstrings(app, what, name, obj, options, lines):
        text = "\n".join(lines)

        # 1) Convert fenced code blocks ```lang ... ``` to RST code-blocks
        def repl_codeblock(match):
            lang = match.group(1) or ""
            code = match.group(2).rstrip()
            if lang:
                header = f".. code-block:: {lang}\n\n"
            else:
                header = "::\n\n"
            indented = "\n".join([f"    {ln}" if ln else "" for ln in code.split("\n")])
            return f"{header}{indented}\n\n"

        codeblock_re = re.compile(
            r"```([a-zA-Z0-9_+-]*)\n([\s\S]*?)\n```",
            re.DOTALL,
        )
        text = codeblock_re.sub(repl_codeblock, text)

        # 2) Convert inline code `x` to RST literals ``x`` (avoid triple/backtick blocks already handled)
        inline_code_re = re.compile(r"`([^`\n]+)`")
        text = inline_code_re.sub(r"``\1``", text)

        # 3) Ensure a blank line after block quotes and directives to avoid "unexpected unindent"
        # Add a blank line after lines ending with '::' if not followed by blank
        colon_re = re.compile(r"(::)\n(\S)")
        text = colon_re.sub(r"\1\n\n\2", text)

        # 4) Balance stray strong markers: replace lone '**' around single words with '**word**'
        # If there is an opening ** without closing before whitespace/newline, escape it
        stray_strong_re = re.compile(r"\*\*(?![^*]+\*\*)")
        text = stray_strong_re.sub(r"\\**", text)

        # 5) Normalize indentation in literal blocks (convert tabs to 4 spaces inside code blocks only)
        def untab_code_blocks(m):
            block = m.group(0)
            return block.replace("\t", "    ")

        untab_re = re.compile(
            r"(?:\n\s*\.\.\s?code-block::[\s\S]*?\n)"
            r"(?:[ ]{0,3}[^\S\n]*\S[\s\S]*?)(?=\n\S|\Z)",
            re.DOTALL,
        )
        text = untab_re.sub(untab_code_blocks, text)

        # 6) Fix section underline lengths like "Title" followed by =====
        def fix_underline(match):
            title = match.group(1)
            underline = match.group(2)
            char = underline.strip()[:1] if underline.strip() else "="
            fixed = char * len(title)
            return f"{title}\n{fixed}\n"

        heading_re = re.compile(r"(^[^\n].*?)\n([=\-~^`:\\+#\*]{2,})\n", re.MULTILINE)
        text = heading_re.sub(fix_underline, text)

        # 7) Ensure blank line before and after section headings
        text = re.sub(r"(\S.*\n[=\-~^`:\\+#\*]{2,}\n)(?!\n)", r"\1\n", text)
        text = re.sub(r"(?<!\n)(\n\S.*\n[=\-~^`:\\+#\*]{2,}\n)", r"\n\1", text)

        # Write back to lines
        lines[:] = text.split("\n")

    app.connect("autodoc-process-docstring", _normalize_markdown_in_docstrings)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
