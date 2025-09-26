#!/bin/bash
# Auto-setup script for pre-commit hooks
# This script automatically installs pre-commit hooks when users clone the repository

set -e

echo "🔧 Setting up pre-commit hooks for ToolUniverse..."

# Check if .pre-commit-config.yaml exists
if [ ! -f ".pre-commit-config.yaml" ]; then
    echo "❌ .pre-commit-config.yaml not found in current directory"
    exit 1
fi

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null; then
    echo "Installing pre-commit..."
    pip install pre-commit
    echo "✅ pre-commit installed successfully"
else
    echo "✅ pre-commit is already installed"
fi

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install
echo "✅ pre-commit hooks installed successfully"

# Update hooks to latest versions
echo "Updating pre-commit hooks..."
pre-commit autoupdate
echo "✅ pre-commit hooks updated successfully"

echo ""
echo "🎉 Pre-commit setup completed successfully!"
echo "📝 Pre-commit hooks will now run automatically on every commit."
echo "💡 To run hooks manually: pre-commit run --all-files"
