Contributing Tools to ToolUniverse
===================================

This section covers how to contribute tools to the ToolUniverse repository. Contributing tools requires additional steps compared to using them locally.

Overview
--------

**Two Types of Tool Contributions:**

1. **Local Tools** - Python classes that run within ToolUniverse
2. **Remote Tools** - MCP servers that run independently

**Key Differences from Self-Use:**

| Aspect | Self-Use | Contributing |
|--------|----------|--------------|
| **Local Tools** | No ``__init__.py`` changes | **Must modify ``__init__.py`` in 4 locations** |
| **Remote Tools** | Local/private deployment | **Must provide public server or deployment docs** |
| **Testing** | Optional | Required (>90% coverage for local, integration for remote) |
| **Documentation** | Optional | Required (docstrings + examples) |
| **Examples** | Optional | Required (in ``examples/`` directory) |
| **Code Quality** | Optional | Required (pre-commit checks) |

Choose Your Tool Type
---------------------

**I want to contribute a Local Tool:**
→ :doc:`local_tools` - Python class that runs in ToolUniverse process

**I want to contribute a Remote Tool:**
→ :doc:`remote_tools` - MCP server that runs independently

**I'm not sure which type to choose:**
→ :doc:`../reference/comparison` - Compare tool types and requirements

Local Tools Contribution
------------------------

**What you need to do:**
1. Create Python class in ``src/tooluniverse/``
2. Use ``@register_tool`` decorator
3. Create JSON config in ``data/xxx_tools.json``
4. **🔑 Modify ``__init__.py`` in 4 locations** (most critical step!)
5. Write tests (>90% coverage)
6. Create examples
7. Submit PR

**Key Requirements:**
- Must modify ``src/tooluniverse/__init__.py`` in 4 specific locations
- Config must be in ``data/`` folder, not in decorator
- Comprehensive testing required
- Examples must be in ``examples/`` directory

**Common Mistakes:**
- Forgetting to modify ``__init__.py`` (tool won't be importable)
- Putting config in decorator instead of JSON file
- Insufficient test coverage

Remote Tools Contribution
-------------------------

**What you need to do:**
1. Create MCP server (any language)
2. Deploy server publicly or provide deployment docs
3. Create JSON config in ``data/remote_tools/xxx_tools.json``
4. Write integration tests
5. Create examples
6. Submit PR

**Key Requirements:**
- Server must be publicly accessible or have detailed deployment docs
- Config must be in ``data/remote_tools/`` folder
- No ``__init__.py`` modifications needed
- Integration testing required

**Common Mistakes:**
- Server not accessible (connection errors)
- Config in wrong location (``data/`` instead of ``data/remote_tools/``)
- Missing deployment documentation

Contribution Process
--------------------

1. **Fork and Clone**
   .. code-block:: bash

      git clone https://github.com/yourusername/ToolUniverse.git
      cd ToolUniverse
      python -m venv venv
      source venv/bin/activate
      pip install -e ".[dev]"
      ./setup_precommit.sh

2. **Develop Your Tool**
   - Follow the specific guide for your tool type
   - Implement all required functionality
   - Add comprehensive tests

3. **Quality Checks**
   - Pre-commit hooks run automatically
   - Ensure all tests pass
   - Verify examples work

4. **Submit PR**
   - Create feature branch
   - Push changes
   - Create pull request with detailed description

5. **Address Feedback**
   - Respond to review comments
   - Make requested changes
   - Update documentation if needed

Code Quality Standards
----------------------

**Required for all contributions:**
- **Code Formatting**: Black formatting (88 character line limit)
- **Linting**: Pass flake8 and ruff checks
- **Type Hints**: Complete type annotations
- **Documentation**: Google-style docstrings with examples
- **Testing**: Comprehensive test coverage
- **Examples**: Working examples in ``examples/`` directory

**Pre-commit Hooks:**
The project uses pre-commit hooks that automatically run:
- Black (code formatting)
- Flake8 (linting)
- Ruff (fast linting)
- Autoflake (import cleanup)
- File validation (YAML, TOML, AST checks)

Testing Requirements
--------------------

**Local Tools:**
- Unit tests with >90% coverage
- Test all public methods
- Test error conditions and edge cases
- Mock external dependencies

**Remote Tools:**
- Integration tests with mocked server
- Test configuration loading
- Test tool discovery and execution
- Test error handling

Documentation Requirements
-------------------------

**Required Documentation:**
- Comprehensive docstrings for all public methods
- Usage examples in docstrings
- README for remote tools (deployment instructions)
- Examples in ``examples/`` directory

**Documentation Standards:**
- Clear, scientist-friendly parameter descriptions
- Real-world usage examples
- Error handling documentation
- Configuration options clearly explained

Getting Help
------------

**Before Contributing:**
- Read the specific guide for your tool type
- Check existing tools for patterns
- Test your tool thoroughly

**During Development:**
- Use GitHub discussions for questions
- Check existing issues for similar problems
- Ask for help early if stuck

**After Submission:**
- Respond promptly to review feedback
- Be open to suggestions and improvements
- Help others by sharing your experience

Resources
---------

- **Local Tools Guide**: :doc:`local_tools`
- **Remote Tools Guide**: :doc:`remote_tools`
- **Tool Comparison**: :doc:`../reference/comparison`
- **Architecture**: :doc:`../reference/architecture`
- **GitHub Repository**: https://github.com/mims-harvard/ToolUniverse
- **Issue Tracker**: https://github.com/mims-harvard/ToolUniverse/issues
- **Discussions**: https://github.com/mims-harvard/ToolUniverse/discussions

Next Steps
----------

Ready to contribute? Choose your path:

* 🏠 **Local Tools**: :doc:`local_tools` - Submit Python tools to ToolUniverse
* 🔗 **Remote Tools**: :doc:`remote_tools` - Submit MCP servers to ToolUniverse
* 🔍 **Compare Types**: :doc:`../reference/comparison` - Understand the differences
* 📚 **Learn First**: :doc:`../quick_start` - Try creating tools before contributing

.. tip::
   **Success Tips**: Start with simple tools, test thoroughly, and don't hesitate to ask for help. The community is here to support you!
