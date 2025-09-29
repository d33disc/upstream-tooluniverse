#!/bin/bash

# ToolUniverse Quick Documentation Generation Script
# This script automatically reads all function docstrings and generates complete API documentation
# Features include:
# 1. Auto-generate tool configuration index
# 2. Generate Remote Tools documentation
# 3. Install Sphinx documentation dependencies
# 4. Generate enhanced API documentation
# 5. Build HTML documentation
# 6. Provide local server preview

# Exit on error (stop script immediately on any error)
set -e

# ===========================================
# Color definitions - for beautifying terminal output
# ===========================================
RED='\033[0;31m'      # Red - error messages
GREEN='\033[0;32m'    # Green - success messages
YELLOW='\033[1;33m'   # Yellow - warning messages
BLUE='\033[0;34m'     # Blue - title messages
PURPLE='\033[0;35m'   # Purple - statistics messages
NC='\033[0m'          # Reset color

# Display script title
echo -e "${BLUE}🧬 ToolUniverse Documentation Generation System${NC}"
echo "========================================"

# Optional strict mode: treat warnings as errors when DOCS_STRICT=1
SPHINX_FLAGS=""
if [ "${DOCS_STRICT}" = "1" ]; then
  SPHINX_FLAGS="-W"
  echo -e "${YELLOW}Strict mode enabled: Sphinx warnings will be treated as errors (-W)${NC}"
fi

# ===========================================
# Directory path settings
# ===========================================
# Get absolute path of script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Project root directory (parent directory of docs)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
# Source code directory
SRC_DIR="$PROJECT_ROOT/src"

echo -e "${YELLOW}Project root directory: ${PROJECT_ROOT}${NC}"
echo -e "${YELLOW}Source code directory: ${SRC_DIR}${NC}"

# ===========================================
# Step 0: Generate tool configuration index (automatic)
# ===========================================
# This step automatically scans all tool configuration files and generates index documentation
echo -e "\n${BLUE}🧩 Generating tool configuration index (automatic)${NC}"
cd "$SCRIPT_DIR"

# Directly call generate_config_index.py to generate tool configuration index
echo -e "${YELLOW}📑 Generating tool configuration index...${NC}"
python generate_config_index.py || { echo -e "${RED}❌ Failed to generate configuration index${NC}"; exit 1; }
echo -e "${GREEN}✅ Tool configuration index generation completed${NC}"

# ===========================================
# Step 0.1: Generate Remote Tools documentation (automatic)
# ===========================================
# This step generates documentation for remote tools, including MCP servers, etc.
echo -e "\n${BLUE}🌐 Generating Remote Tools documentation (automatic)${NC}"
cd "$SCRIPT_DIR"

# Check if remote tool documentation generation script exists
if [ -f "generate_remote_tools_docs.py" ]; then
    python generate_remote_tools_docs.py || { echo -e "${RED}❌ Failed to generate Remote Tools documentation${NC}"; exit 1; }
    echo -e "${GREEN}✅ Remote Tools documentation generation completed${NC}"
else
    echo -e "${YELLOW}⚠️ generate_remote_tools_docs.py not found${NC}"
fi

# ===========================================
# Step 1: Install Sphinx documentation dependencies
# ===========================================
# Install Python packages required for building documentation
echo -e "\n${BLUE}📦 Installing enhanced documentation dependencies${NC}"
cd "$PROJECT_ROOT"

# Prefer local virtualenv if exists; otherwise, create one for isolation
if [ -d ".venv" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate || true
else
  if command -v python3 >/dev/null 2>&1; then
    python3 -m venv .venv || true
    # shellcheck disable=SC1091
    source .venv/bin/activate || true
  fi
fi

# Install via project extras if possible; fallback to explicit list
if command -v uv >/dev/null 2>&1; then
  uv pip install -q -e '.[docs]' 2>/dev/null || uv pip install -q sphinx furo myst-parser linkify-it-py sphinx-copybutton sphinx-design sphinx-tabs sphinx-notfound-page sphinx-autodoc-typehints 2>/dev/null || true
else
  pip install -q -e '.[docs]' 2>/dev/null || pip install -q sphinx furo myst-parser linkify-it-py sphinx-copybutton sphinx-design sphinx-tabs sphinx-notfound-page sphinx-autodoc-typehints 2>/dev/null || true
fi
echo -e "${GREEN}✅ Dependencies installation completed${NC}"

# ===========================================
# Step 2: Generate enhanced API documentation
# ===========================================
# Use sphinx-apidoc to automatically scan Python source code and generate API documentation
echo -e "\n${BLUE}📋 Generating enhanced API documentation${NC}"
cd "$SCRIPT_DIR"

# ===========================================
# Clean old build files
# ===========================================
# Clean build directory
if [ -d "_build" ]; then rm -rf _build; fi

# Note: Keep api directory as it may contain manually generated documentation
# If complete regeneration is needed, uncomment the line below
# if [ -d "api" ]; then rm -rf api; fi

# Clean template directory
if [ -d "_templates" ]; then rm -rf _templates; fi

# ===========================================
# Create custom template directory and files
# ===========================================
# Create template directory
mkdir -p _templates

# Create function documentation template
cat > _templates/function.rst << 'EOF'
{{ fullname }}
{{ underline }}

.. currentmodule:: {{ module }}

.. autofunction:: {{ objname }}
EOF

# Create class documentation template
cat > _templates/class.rst << 'EOF'
{{ fullname }}
{{ underline }}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__,__call__,__str__,__repr__
EOF

# Create module documentation template
cat > _templates/module.rst << 'EOF'
{{ fullname }}
{{ underline }}

.. currentmodule:: {{ module }}

.. automodule:: {{ objname }}
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__,__call__,__str__,__repr__
   :imported-members:
EOF

# Ensure api directory exists
mkdir -p api

# ===========================================
# Use sphinx-apidoc to generate API documentation
# ===========================================
# Check if sphinx-apidoc command is available
if command -v sphinx-apidoc >/dev/null 2>&1; then
    # Use sphinx-apidoc to scan source code and generate API documentation
    # -f: force overwrite existing files
    # -o api: output to api directory
    # ../src/tooluniverse: source code path
    # --separate: create separate documentation file for each module
    # --module-first: module name first
    # --maxdepth 6: maximum recursion depth
    # --private: include private members
    # --force: force regeneration
    # --templatedir=_templates: use custom templates
    sphinx-apidoc -f -o api ../src/tooluniverse \
        --separate \
        --module-first \
        --maxdepth 6 \
        --private \
        --force \
        --templatedir=_templates \
        2>/dev/null || true

    # Count generated API documentation files
    API_FILES=$(find api -name "*.rst" | wc -l | tr -d ' ')
    echo -e "${GREEN}✅ Generated ${API_FILES} API documentation files${NC}"

    # ===========================================
    # Display discovered module information
    # ===========================================
    echo -e "\n${PURPLE}📋 Discovered modules:${NC}"
    find api -name "*.rst" | sed 's|api/||' | sed 's|\.rst$||' | sort | head -20 | while read -r module; do
        echo -e "   📄 ${module}"
    done
    
    # If module count exceeds 20, show remaining count
    REMAINING=$(find api -name "*.rst" | wc -l | tr -d ' ')
    if [ "$REMAINING" -gt 20 ]; then
        echo -e "   ... and $((REMAINING - 20)) more modules"
    fi

    # ===========================================
    # Generate module discovery report
    # ===========================================
    echo -e "\n${PURPLE}📋 Module discovery report:${NC}"
    echo -e "   🔍 Core modules: $(find "$SRC_DIR/tooluniverse" -maxdepth 1 -name "*.py" | wc -l | tr -d ' ')"
    echo -e "   🔍 Compose scripts: $(find "$SRC_DIR/tooluniverse/compose_scripts" -name "*.py" 2>/dev/null | wc -l | tr -d ' ' || echo "0")"
    echo -e "   🔍 External tools: $(find "$SRC_DIR/tooluniverse/external" -name "*.py" 2>/dev/null | wc -l | tr -d ' ' || echo "0")"
    echo -e "   🔍 Tool scripts: $(find "$SRC_DIR/tooluniverse/scripts" -name "*.py" 2>/dev/null | wc -l | tr -d ' ' || echo "0")"
else
    echo -e "${RED}❌ sphinx-apidoc not found${NC}"
    exit 1
fi

# ===========================================
# Step 3: Build enhanced HTML documentation
# ===========================================
# Use sphinx-build to convert RST documentation to HTML format
echo -e "\n${BLUE}🔧 Building enhanced HTML documentation${NC}"

# Ensure Python can import project sources when building
export PYTHONPATH="$SRC_DIR:$PYTHONPATH"

# Use sphinx-build to build HTML documentation
# -b html: build HTML format
# . : current directory (docs directory)
# _build/html: output directory
# --keep-going: continue building when encountering errors
# -q: quiet mode
sphinx-build ${SPHINX_FLAGS} -b html . _build/html --keep-going -q || true

# ===========================================
# Check build results
# ===========================================
# Check if homepage file was successfully generated
if [ -f "_build/html/index.html" ]; then
    echo -e "${GREEN}✅ Documentation build successful${NC}"
else
    echo -e "${RED}❌ Documentation build failed${NC}"
    exit 1
fi

# ===========================================
# Step 4: Generate detailed statistics
# ===========================================
# Count generated documentation files and code statistics
echo -e "\n${BLUE}📊 Generating detailed statistics${NC}"

# Count HTML files
HTML_FILES=$(find _build/html -name "*.html" | wc -l | tr -d ' ')
# Count API documentation
API_DOCS=$(find _build/html/api -name "*.html" 2>/dev/null | wc -l | tr -d ' ' || echo "0")
# Calculate total documentation size
DOC_SIZE=$(du -sh _build/html 2>/dev/null | cut -f1 || echo "unknown")

# ===========================================
# Count source code information
# ===========================================
# Count function count
FUNCTION_COUNT=$(grep -r "def " "$SRC_DIR" --include="*.py" | wc -l | tr -d ' ')
# Count class count
CLASS_COUNT=$(grep -r "class " "$SRC_DIR" --include="*.py" | wc -l | tr -d ' ')
# Count module count
MODULE_COUNT=$(find "$SRC_DIR" -name "*.py" | wc -l | tr -d ' ')

# ===========================================
# Display statistics results
# ===========================================
echo -e "\n${GREEN}🎉 Enhanced documentation generation completed!${NC}"
echo -e "${BLUE}📊 Detailed statistics:${NC}"
echo -e "   📄 HTML files: ${HTML_FILES}"
echo -e "   🔧 API documentation: ${API_DOCS}"
echo -e "   📁 Total size: ${DOC_SIZE}"
echo -e "   🐍 Python modules: ${MODULE_COUNT}"
echo -e "   🔧 Total functions: ${FUNCTION_COUNT}"
echo -e "   🏗️ Total classes: ${CLASS_COUNT}"

# ===========================================
# Step 5: Display documentation access methods
# ===========================================
# Provide various ways to access documentation and links
BUILD_PATH="$SCRIPT_DIR/_build/html/index.html"
echo -e "\n${BLUE}📂 Access documentation:${NC}"
echo -e "   🏠 Homepage: file://${BUILD_PATH}"
echo -e "   🔧 Complete API: file://${SCRIPT_DIR}/_build/html/api/modules.html"

# ===========================================
# Step 6: Optional local server startup
# ===========================================
# Check if running in CI environment
if [ -n "$CI" ] || [ -n "$GITHUB_ACTIONS" ]; then
    echo -e "${BLUE}🤖 CI environment detected, skipping server startup${NC}"
else
    # Ask user if they want to start local HTTP server to preview documentation
    echo -e "\n${YELLOW}Start local server to view documentation? (y/n)${NC}"
    read -r response

    # If user chooses to start server
    if [[ "$response" =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}🚀 Starting server...${NC}"

    # ===========================================
    # Port detection and allocation
    # ===========================================
    # Try different ports to find available port
    PORTS=(8080 8081 8082 8083 8084)
    PORT=""

    # Iterate through port list to find first available port
    for p in "${PORTS[@]}"; do
        if ! lsof -Pi :$p -sTCP:LISTEN -t >/dev/null 2>&1; then
            PORT=$p
            break
        fi
    done

    # ===========================================
    # Start HTTP server
    # ===========================================
    if [ -z "$PORT" ]; then
        # If no available port found, provide manual startup command
        echo -e "${RED}❌ Unable to find available port, please start server manually${NC}"
        echo -e "${YELLOW}💡 Manual startup command: cd _build/html && python -m http.server 8080${NC}"
    else
        # Display access address
        echo -e "${GREEN}📡 Access address: http://localhost:${PORT}${NC}"
        echo -e "${YELLOW}Press Ctrl+C to stop server${NC}"

        # Switch to build directory and start server
        cd _build/html
        python -m http.server $PORT
    fi
fi
fi

# ===========================================
# Script completion summary
# ===========================================
# Display script execution completion and new features introduction
echo -e "\n${GREEN}✅ Enhanced documentation system completed!${NC}"
echo -e "${BLUE}💡 New features:${NC}"
echo -e "   ✨ Automatic discovery of all modules and functions"
echo -e "   📊 Detailed statistics"
echo -e "   🔍 Enhanced module discovery"
echo -e "   📚 Comprehensive API index"
echo -e "   🎨 Custom template support"
echo -e "   📱 Responsive design"
echo -e "   🔍 Built-in search functionality"