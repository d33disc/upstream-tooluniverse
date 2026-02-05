Installation
==================

**Complete installation options for ToolUniverse**

This Tutorial covers all installation methods and environment setup options.

System Requirements
-------------------

* Python 3.10 or higher
* uv package manager (recommended) or pip
* Internet connection for API access
* GPU for machine learning models (optional)
* API keys for external services (optional)

Installation Methods
--------------------

Choose the installation method that best fits your needs:

.. tabs::

   .. tab:: 📦 PyPI Installation

      Install ToolUniverse using pip:

      .. code-block:: bash

         pip install tooluniverse

      **Install with Optional Dependencies (pip)**

      For enhanced functionality:

      .. code-block:: bash

         pip install tooluniverse[dev]
         pip install tooluniverse[embedding]
         pip install tooluniverse[all]

      **Verify Installation**

      .. code-block:: python

         import tooluniverse
         print(f"ToolUniverse version: {tooluniverse.__version__}")
         print("✅ Installation successful!")

      **Test MCP Server**

      .. code-block:: bash

         # Test MCP Server (default port 8000)
         tooluniverse-smcp --help

   .. tab:: 🔧 Development Installation

      **Best for**: Contributors, custom modifications

      **Clone and Install from Source (Recommended with uv)**

      For development or custom modifications:

      .. code-block:: bash

         # Clone the repository
         git clone https://github.com/mims-harvard/ToolUniverse.git

         # Add all dependencies
         uv sync

      **Alternative: Clone and Install from Source (pip)**

      For development or custom modifications:

      .. code-block:: bash

         # Clone the repository
         git clone https://github.com/mims-harvard/ToolUniverse.git

         # Install in editable mode
         pip install -e .

         # Install development dependencies
         pip install -e .[dev]

         # Auto-setup pre-commit hooks (recommended)
         ./setup_precommit.sh

      **Alternative: Development Setup with Virtual Environment (pip)**

      .. code-block:: bash

         # Create virtual environment
         python -m venv tooluniverse-env
         source tooluniverse-env/bin/activate  # On Windows: tooluniverse-env\Scripts\activate

         # Install in development mode
         pip install -e .[dev]

         # Auto-setup pre-commit hooks (recommended)
         ./setup_precommit.sh

   .. tab:: 🐳 Container Installation

      **Best for**: Isolated environments, CI/CD

      **Docker Installation**

      Create a Dockerfile:

      .. code-block:: dockerfile

         FROM python:3.10-slim

         WORKDIR /app
         COPY requirements.txt .
         RUN pip install -r requirements.txt
         RUN pip install tooluniverse

         CMD ["tooluniverse-smcp", "--host", "0.0.0.0", "--port", "7000"]

      **Docker Compose**

      .. code-block:: yaml

         version: '3.8'
         services:
           tooluniverse:
             build: .
             ports:
               - "7000:7000"
             environment:
               - OPENTARGETS_API_KEY=${OPENTARGETS_API_KEY}
               - NCBI_API_KEY=${NCBI_API_KEY}
             volumes:
               - ./data:/app/data

Environment Configuration
-------------------------

**API Keys and Authentication**

ToolUniverse supports 1000+ scientific tools. Some require API keys for access, while others benefit from API keys through higher rate limits.

For comprehensive information about API keys, including:

* Which APIs are required vs optional
* How to obtain each API key
* Rate limits with and without keys
* Configuration methods and best practices

See the dedicated :doc:`api_keys` documentation.

**Quick Start - Essential API Keys**

Required for specific features:

.. code-block:: bash

   # Structure prediction & molecular modeling (NVIDIA NIM)
   NVIDIA_API_KEY=your_nvidia_key_here

   # Patent data (USPTO)
   USPTO_API_KEY=your_uspto_key_here

   # Model hosting (Hugging Face)
   HF_TOKEN=your_huggingface_token_here

**Recommended for Better Performance**

.. code-block:: bash

   # Higher rate limits for common databases (set once, used everywhere)
   NCBI_API_KEY=your_ncbi_key_here              # 3x faster PubMed/sequence queries
   SEMANTIC_SCHOLAR_API_KEY=your_key_here       # 100x faster literature search
   FDA_API_KEY=your_fda_key_here                # 6x faster drug safety queries

   # Note: NCBI and Semantic Scholar keys can also be passed as tool parameters
   # for per-call control, but environment variables are more convenient

**Using a .env File**

Create a ``.env`` file in your project directory:

.. code-block:: bash

   # Copy the template
   cp docs/.env.template .env

   # Edit with your API keys
   nano .env

See :doc:`api_keys` for complete configuration details and all available API keys.


Dependencies
------------



ToolUniverse automatically installs core dependencies.

Install additional features:

.. code-block:: bash

   # Development tools (uv - recommended)
   uv add "tooluniverse[dev]" --dev

   # Embedding functionality (uv - recommended)
   uv add "tooluniverse[embedding]" --dev

   # All optional dependencies (uv - recommended)
   uv add "tooluniverse[all]" --dev

   # Alternative with pip
   pip install tooluniverse[dev]
   pip install tooluniverse[embedding]
   pip install tooluniverse[all]


Verification
------------

Verify your installation:

.. code-block:: python

   import tooluniverse
   print(f"ToolUniverse version: {tooluniverse.__version__}")
   print("✅ Installation successful!")

Test MCP Server:

.. code-block:: bash

   # Test MCP server
   tooluniverse-smcp --help

   # Start MCP server
   tooluniverse-smcp

Test Basic Functionality:

.. code-block:: python

   from tooluniverse import ToolUniverse

   # Initialize and test
   tu = ToolUniverse()
   tu.load_tools()
   print(f"✅ Loaded {len(tu.all_tools)} tools successfully!")

What's Next?
------------

Now that ToolUniverse is installed, you're ready to start using it!

**Recommended next steps**:

1. **Try the Quickstart** (:doc:`quickstart`) - Run your first query in 5 minutes
2. **Follow the Tutorial** (:doc:`getting_started`) - Step-by-step guide to core features
3. **Integrate with AI Assistants** (:doc:`guide/building_ai_scientists/index`) - Connect to Claude, ChatGPT, or Gemini
4. **Explore Available Tools** (:doc:`tools/tools_config_index`) - Browse 1000+ scientific tools
5. **Configure API Keys** (:doc:`api_keys`) - Optional: Set up API keys for enhanced performance

**Need help?** See :doc:`help/troubleshooting` or :doc:`help/faq`.

Troubleshooting
---------------

ImportError: No module named 'tooluniverse':

.. code-block:: bash

   # Check Python environment
   which python
   pip list | grep tooluniverse

   # Reinstall if needed
   pip uninstall tooluniverse
   pip install tooluniverse

Permission Denied Errors:

.. code-block:: bash

   # Use user installation (pip)
   pip install --user tooluniverse

   # Or use virtual environment (pip)
   python -m venv venv
   source venv/bin/activate
   pip install tooluniverse

   # Or use uv (recommended - handles permissions automatically)
   uv add tooluniverse --dev

**Getting Help**

If you encounter issues:

1. Check the `GitHub Issues <https://github.com/mims-harvard/ToolUniverse/issues>`_
2. Review the documentation
3. Create a new issue with detailed error information
4. Include system information and error logs