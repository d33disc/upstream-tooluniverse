Documentation Deployment
========================

This guide covers how to build and deploy the ToolUniverse documentation.

Local Development
-----------------

Build documentation locally:

.. code-block:: bash

   cd docs/
   ./quick_doc_build.sh

Start local server:

.. code-block:: bash

   make serve
   # or
   make livehtml

Access documentation at: http://localhost:8000

GitHub Pages (Automatic)
------------------------

The documentation is automatically deployed to GitHub Pages when you push to the main branch.

**Setup:**
1. Enable GitHub Pages in repository settings (Settings > Pages > Source: GitHub Actions)
2. Push changes to main branch
3. Documentation builds automatically

**Access:** https://yourusername.github.io/ToolUniverse/

Available Make Commands
-----------------------

.. code-block:: bash

   make clean      # Clean build files
   make html       # Build HTML documentation
   make serve      # Start local server
   make livehtml   # Auto-rebuild on changes
   make clean-html # Clean only HTML files