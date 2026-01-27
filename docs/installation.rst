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
         tooluniverse-mcp --help

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

**Environment Variables**

Set up API keys for enhanced functionality:

.. code-block:: bash

   # Optional API keys for better performance
   # Required API Keys
   USPTO_API_KEY=your_uspto_key_here
   HF_TOKEN=your_huggingface_token_here
   NVIDIA_API_KEY=your_nvidia_key_here

   # MCP Server Hosts
   USPTO_MCP_SERVER_HOST=full_url_of_uspto_mcp_server
   BOLTZ_MCP_SERVER_HOST=full_url_of_boltz_mcp_server
   TXAGENT_MCP_SERVER_HOST=full_url_of_txagent_mcp_server
   EXPERT_FEEDBACK_MCP_SERVER_URL=http://localhost:9877

   # Optional API Keys (for enhanced features)
   OPENAI_API_KEY=your_openai_key_here
   AZURE_OPENAI_API_KEY=your_azure_key_here
   GEMINI_API_KEY=your_gemini_key_here
   FDA_API_KEY=your_fda_key_here
   OPENTARGETS_API_KEY=your_opentargets_key_here
   NCBI_API_KEY=your_ncbi_key_here
   SEMANTIC_SCHOLAR_API_KEY=your_semantic_scholar_key_here

   # Additional Configuration
   OPENAI_BASE_URL=https://api.openai.com/v1
   AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com
   AZURE_OPENAI_API_VERSION=version_of_your_azure_api


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