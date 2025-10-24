Contributing Tools to ToolUniverse
==================================================

This comprehensive Tutorial covers everything you need to know about contributing tools to ToolUniverse, from understanding existing tools to creating, testing, and submitting your own tools.

Table of Contents
-----------------

.. contents::
   :local:
   :depth: 3

Part I: Understanding ToolUniverse Tools
========================================

What Are ToolUniverse Tools?
----------------------------

ToolUniverse tools are standardized interfaces to scientific databases, APIs, machine learning models, and data analysis packages. Each tool follows a consistent pattern:

- **Standardized Input/Output**: All tools accept structured parameters and return consistent JSON responses
- **Error Handling**: Unified error reporting across all tools
- **Documentation**: Self-describing with clear parameter specifications
- **Testing**: Comprehensive test coverage for reliability


Part II: Step-by-Step Tool Development Tutorial
============================================

Step 1: Development Environment Setup
-------------------------------------

1.1 Fork and Clone Repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Fork the repository on GitHub first
   git clone https://github.com/yourusername/ToolUniverse.git
   cd ToolUniverse

1.2 Create Virtual Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

1.3 Install Development Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install -e ".[dev]"

1.4 Install Pre-commit Hooks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Automatic Setup (Recommended):**

.. code-block:: bash

   # Auto-install pre-commit hooks
   ./setup_precommit.sh

**Manual Setup:**

.. code-block:: bash

   # Install pre-commit if not already installed
   pip install pre-commit
   
   # Install hooks
   pre-commit install
   
   # Update to latest versions
   pre-commit autoupdate

**Required Development Tools:**
- ``pytest`` - Testing framework
- ``black`` - Code formatting
- ``flake8`` - Code linting
- ``mypy`` - Type checking
- ``sphinx`` - Documentation
- ``pre-commit`` - Git hooks

**Pre-commit Benefits:**
- ✅ **Automatic code formatting** with Black
- ✅ **Code linting** with flake8 and ruff
- ✅ **Import cleanup** with autoflake
- ✅ **File validation** (YAML, TOML, AST checks)
- ✅ **Runs on every commit** to ensure code quality

Step 2: Choose Your Tool Type and Design
----------------------------------------

2.1 Tool Type Selection
~~~~~~~~~~~~~~~~~~~~~~~

Before implementing, decide whether your tool should be local or remote:

**Local Tools** (recommended for most cases):
- Python classes running in the same process
- Best for: API wrappers, data processing, simple computations
- See :doc:`local_tool_registration` for detailed implementation Tutorial

**Remote Tools** (for specialized cases):
- External services accessed via MCP or REST APIs
- Best for: microservices, cloud AI services, existing systems
- See :doc:`remote_tool_registration` for detailed implementation Tutorial

2.2 Research Your Data Source
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **API Documentation**: Understand endpoints, rate limits, authentication
- **Data Format**: Study response structures and data types
- **Error Conditions**: Identify common error scenarios
- **Usage Patterns**: How researchers typically use this data

**Design Principles:**
- Keep parameters intuitive for scientists
- Use consistent naming conventions
- Provide sensible defaults
- Support common use cases first

Step 3: Tool Implementation
---------------------------

The implementation details depend on whether you're creating a local or remote tool:

**For Local Tools:**
Follow the comprehensive Tutorial at :doc:`local_tool_registration` which covers:
- Directory structure and file organization
- Tool class implementation with BaseTool inheritance
- Configuration and parameter handling
- Testing and validation

**For Remote Tools:**
Follow the detailed Tutorial at :doc:`remote_tool_registration` which covers:
- MCP server setup and configuration
- REST API wrapper patterns
- Authentication and security
- Performance optimization

**Key Requirements for Community Contribution:**

1. **Inherit from BaseTool**: All contributed tools must inherit from BaseTool
2. **Comprehensive Documentation**: Include detailed docstrings with examples
3. **Error Handling**: Implement robust error handling and validation
4. **Consistent API**: Follow ToolUniverse conventions for parameters and responses
5. **Scientific Focus**: Design interfaces that are intuitive for researchers

For detailed implementation examples and templates, see the appropriate Tutorial above.

3.3 Contribution-Specific Requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When contributing tools to ToolUniverse, ensure your implementation includes:

**Code Organization:**
- Place tools in appropriate domain directories
- Include comprehensive test suites with >90% coverage
- Provide configuration files following ToolUniverse standards
- Add proper documentation and examples

**Quality Standards:**
- Pass all code quality checks (Black, flake8, mypy)
- Include detailed docstrings with usage examples
- Implement robust error handling and input validation
- Follow scientific naming conventions

For detailed file structures and templates, refer to the tool registration guides linked above.

Step 4: Testing Requirements for Contribution
---------------------------------------------

Contributors must provide comprehensive test suites. The testing patterns and examples are detailed in :doc:`local_tool_registration` under the testing section.

**Key Testing Requirements:**

- **>90% Test Coverage**: All contributed tools must have comprehensive test coverage
- **Unit Tests**: Test all public methods with various inputs and edge cases
- **Integration Tests**: Verify tool works correctly within ToolUniverse
- **Error Testing**: Test all error conditions and input validation
- **Mock External APIs**: Use mocks for external service calls in tests

**Required Test Components:**
- Test class with pytest fixtures
- Mock external API calls appropriately
- Test both success and error scenarios
- Include test data fixtures
- Validate input/output formats

For detailed testing examples and templates, see :doc:`local_tool_registration` which includes:
- Complete test file structures
- Fixture creation patterns
- Mocking strategies for external APIs
- Coverage reporting setup

Step 5: Code Quality and Standards for Contribution
---------------------------------------------------

All contributed tools must meet ToolUniverse's code quality standards. The detailed requirements and examples are covered in :doc:`local_tool_registration`.

**Quality Checklist:**

5.1 Pre-submission Requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Format code with Black
   black src/tooluniverse/tools/your_domain/

   # Check linting with flake8
   flake8 src/tooluniverse/tools/your_domain/

   # Verify type hints with mypy
   mypy src/tooluniverse/tools/your_domain/

   # Run tests with coverage
   pytest --cov=tooluniverse src/tooluniverse/tools/your_domain/tests/

**Required Standards:**
- **Code Formatting**: Black formatting (88 character line limit)
- **Linting**: Pass flake8 checks with no warnings
- **Type Hints**: All functions must have complete type annotations
- **Documentation**: Google-style docstrings with examples
- **Testing**: >90% test coverage

For detailed code examples and documentation templates, see :doc:`local_tool_registration`.

Step 6: Tool Registration and Discovery
---------------------------------------

Tool registration is handled automatically by ToolUniverse when tools are placed in the correct directory structure. The registration details are covered in the implementation guides:

- **Local Tools**: See :doc:`local_tool_registration` for automatic discovery patterns
- **Remote Tools**: See :doc:`remote_tool_registration` for MCP and REST API registration

**Verification Test:**

.. code-block:: python

   # Verify your tool is properly registered
   from tooluniverse import ToolUniverse

   tu = ToolUniverse()
   tu.load_tools()

   # Check tool is discovered
   tools = tu.list_tools()
   assert "YourToolName" in tools

   # Test basic functionality
   result = tu.run_one_function({
       "name": "your_tool_name",
       "arguments": {"test_param": "test_value"}
   })
   print(f"Tool test result: {result}")

Step 7: Documentation Requirements for Contribution
---------------------------------------------------

Contributors must provide comprehensive documentation for their tools. The detailed documentation patterns and requirements are covered in :doc:`local_tool_registration`.

**Required Documentation Components:**

- **Comprehensive Docstrings**: All public methods must have detailed Google-style docstrings
- **Usage Examples**: Include practical examples in docstrings showing real-world usage
- **API Documentation**: Create RST documentation files for Sphinx if contributing to core
- **README Updates**: Update relevant documentation to mention your tool's capabilities

**Documentation Standards:**
- Clear, scientist-friendly parameter descriptions
- Real-world usage examples in docstrings
- Error handling documentation
- Configuration options clearly explained

For detailed documentation templates and examples, see :doc:`local_tool_registration` which includes complete documentation patterns and Sphinx integration examples.

Step 8: Integration Testing for Contribution
--------------------------------------------

Before submitting your tool, verify it integrates correctly with ToolUniverse through integration testing.

**Required Integration Tests:**

.. code-block:: python

   # Verify tool loads and integrates correctly
   from tooluniverse import ToolUniverse

   def test_tool_integration():
       """Test tool integration with ToolUniverse."""
       tu = ToolUniverse()
       tu.load_tools()

       # Verify tool is discovered
       tools = tu.list_tools()
       assert "YourToolName" in tools

       # Test basic functionality
       result = tu.run_one_function({
           "name": "your_tool_name",
           "arguments": {"test_param": "test_value"}
       })

       # Verify response format
       assert "status" in result
       assert result["status"] in ["success", "error"]

**Integration Test Requirements:**
- **Tool Discovery**: Verify tool is automatically discovered by ToolUniverse
- **API Compliance**: Ensure tool methods work through ToolUniverse interface
- **Response Format**: Validate standardized response structure
- **Error Handling**: Test error conditions are properly handled

The detailed integration testing patterns are covered in :doc:`local_tool_registration`.

Step 9: Pull Request Submission
-------------------------------

9.1 Pre-submission Checklist
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before submitting your pull request, ensure:

**Code Quality:**
- [ ] All tests pass: ``pytest``
- [ ] Code is formatted: ``black src/``
- [ ] No linting errors: ``flake8 src/``
- [ ] Type checking passes: ``mypy src/``
- [ ] Test coverage >90%: ``pytest --cov=tooluniverse``

**Documentation:**
- [ ] Docstrings follow Google style
- [ ] API documentation is complete
- [ ] Usage examples are provided
- [ ] README updated if needed

**Testing:**
- [ ] Unit tests cover all methods
- [ ] Integration tests pass
- [ ] Error conditions are tested
- [ ] Edge cases are handled

**Tool Integration:**
- [ ] Tool loads correctly in ToolUniverse
- [ ] Tool methods work through ToolUniverse interface
- [ ] Configuration is properly handled

9.2 Create Feature Branch
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Create and switch to feature branch
   git checkout -b feature/add-your-tool-name

   # Make your changes (already done above)

   # Add all new files
   git add src/tooluniverse/tools/your_domain/
   git add examples/your_domain/
   git add tests/integration/test_your_tool_integration.py
   git add docs/tools/your_domain.rst

9.3 Commit Changes
~~~~~~~~~~~~~~~~~~

Use conventional commit messages:

.. code-block:: bash

   git commit -m "feat: add YourToolName for [data source] access

   - Implement YourToolName class with search and details methods
   - Add comprehensive unit tests with >95% coverage
   - Include integration tests for ToolUniverse compatibility
   - Add API documentation and usage examples
   - Support for configurable API endpoints and authentication

   Closes #[issue-number]"

**Commit Message Format:**
- ``feat``: New tool or feature
- ``fix``: Bug fixes
- ``docs``: Documentation updates
- ``test``: Test additions
- ``refactor``: Code refactoring

9.4 Push and Create PR
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Push feature branch
   git push origin feature/add-your-tool-name

**Pull Request Template:**

.. code-block:: markdown

   ## Description

   This PR adds YourToolName, a new tool for accessing [Data Source Name] API. The tool provides functionality to:

   - Search for entities using natural language queries
   - Retrieve detailed information about specific entities
   - Handle API errors gracefully with meaningful error messages

   ## Changes Made

   - ✅ **Tool Implementation**: Complete YourToolName class with all required methods
   - ✅ **Testing**: Unit tests with 95% coverage + integration tests
   - ✅ **Documentation**: Comprehensive API docs and usage examples
   - ✅ **Configuration**: Support for custom API endpoints and authentication
   - ✅ **Error Handling**: Robust error handling with detailed error messages

   ## Data Source Information

   - **API**: [Data Source Name] API v2.0
   - **Documentation**: https://docs.example.com/api
   - **Rate Limits**: 60 requests/minute, 1000 requests/hour
   - **Authentication**: Optional API key
   - **Data Coverage**: [Describe what data this covers]

   ## Testing

   ```bash
   # Run tool-specific tests
   pytest src/tooluniverse/tools/your_domain/tests/

   # Run integration tests
   pytest tests/integration/test_your_tool_integration.py

   # Test through ToolUniverse interface
   python examples/your_domain/basic_usage.py
   ```

   ## Breaking Changes

   None - this is a new tool addition.

   ## Related Issues

   Closes #[issue-number]

   ## Checklist

   - [x] Tests pass locally
   - [x] Code follows project style guidelines
   - [x] Documentation is complete and accurate
   - [x] No breaking changes to existing tools
   - [x] Tool integrates correctly with ToolUniverse
   - [x] Examples work as expected

Step 10: Post-Submission
------------------------

10.1 Respond to Review Feedback
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Common Review Feedback:**

1. **Code Style Issues**
   - Fix formatting, linting, or type hint issues
   - Follow naming conventions
   - Improve code organization

2. **Testing Improvements**
   - Add missing test cases
   - Improve test coverage
   - Mock external dependencies properly

3. **Documentation Clarifications**
   - Clarify unclear docstrings
   - Add missing examples
   - Fix documentation formatting

4. **API Design Suggestions**
   - Simplify complex interfaces
   - Make parameters more intuitive
   - Improve error messages

**How to Address Feedback:**

.. code-block:: bash

   # Make requested changes
   # ... edit files ...

   # Test changes
   pytest
   black src/
   flake8 src/

   # Commit fixes
   git add .
   git commit -m "fix: address review feedback

   - Improve error message clarity
   - Add missing test cases for edge conditions
   - Fix docstring formatting issues
   - Simplify configuration parameter names"

   # Push updates
   git push origin feature/add-your-tool-name

10.2 Tool Maintenance
~~~~~~~~~~~~~~~~~~~~~

After your tool is merged:

**Ongoing Responsibilities:**
- Monitor for issues reported by users
- Update tool when external API changes
- Improve performance based on usage patterns
- Add new features as requested by community

**Version Updates:**
- Follow semantic versioning for tool updates
- Document breaking changes clearly
- Provide migration guides when needed

Part III: Advanced Topics
=========================

Tool Composition and Workflows
------------------------------

Design your tool to work well with others:

.. code-block:: python

   # Example: Design tools that output data usable by other tools
   def search_entities(self, query: str) -> Dict[str, Any]:
       """Return entity IDs that other tools can use."""
       return {
           "status": "success",
           "data": [
               {
                   "id": "ENTITY_123",  # Other tools can use this ID
                   "name": "Entity Name",
                   "type": "protein",   # Other tools can filter by type
                   "references": ["PMID:12345"]  # Literature tools can use these
               }
           ]
       }

Performance Optimization
------------------------

**Caching Strategies:**

.. code-block:: python

   from functools import lru_cache
   import hashlib

   class OptimizedTool(BaseTool):

       @lru_cache(maxsize=100)
       def _cached_api_call(self, query_hash: str, params_hash: str):
           """Cache expensive API calls."""
           # Implementation here
           pass

       def search_entities(self, query: str, **kwargs):
           # Create cache keys
           query_hash = hashlib.md5(query.encode()).hexdigest()
           params_hash = hashlib.md5(str(sorted(kwargs.items())).encode()).hexdigest()

           return self._cached_api_call(query_hash, params_hash)

**Batch Processing:**

.. code-block:: python

   def batch_process_entities(self, entity_ids: List[str]) -> List[Dict[str, Any]]:
       """Process multiple entities efficiently."""
       # Batch API calls instead of individual requests
       batch_size = 50
       results = []

       for i in range(0, len(entity_ids), batch_size):
           batch = entity_ids[i:i + batch_size]
           batch_results = self._api_batch_call(batch)
           results.extend(batch_results)

       return results

Security Considerations
-----------------------

**API Key Handling:**

.. code-block:: python

   import os
   from typing import Optional

   class SecureTool(BaseTool):

       def __init__(self, config: Dict[str, Any] = None):
           super().__init__(config)

           # Get API key from environment variable or config
           self.api_key = self._get_secure_api_key()

       def _get_secure_api_key(self) -> Optional[str]:
           """Securely retrieve API key."""
           # Priority: config > environment > None
           if self.config and "api_key" in self.config:
               return self.config["api_key"]

           return os.getenv("YOUR_TOOL_API_KEY")

       def _make_authenticated_request(self, endpoint: str, **kwargs):
           """Make request with secure authentication."""
           headers = kwargs.get("headers", {})

           if self.api_key:
               headers["Authorization"] = f"Bearer {self.api_key}"
           else:
               # Handle unauthenticated access gracefully
               headers["User-Agent"] = "ToolUniverse/1.0"

           kwargs["headers"] = headers
           return self._make_request(endpoint, **kwargs)

**Input Sanitization:**

.. code-block:: python

   import re
   from typing import Any

   def _sanitize_query(self, query: str) -> str:
       """Sanitize user input to prevent injection attacks."""
       # Remove potentially dangerous characters
       sanitized = re.sub(r'[<>&"\'\\]', '', query)

       # Limit length
       if len(sanitized) > 1000:
           raise ValueError("Query too long (max 1000 characters)")

       return sanitized.strip()

Error Recovery and Resilience
-----------------------------

**Retry Logic:**

.. code-block:: python

   import time
   from typing import Callable, Any

   def _retry_with_backoff(
       self,
       func: Callable,
       max_retries: int = 3,
       backoff_factor: float = 2.0
   ) -> Any:
       """Retry function with exponential backoff."""
       for attempt in range(max_retries):
           try:
               return func()
           except (requests.exceptions.ConnectionError,
                   requests.exceptions.Timeout) as e:
               if attempt == max_retries - 1:
                   raise e

               wait_time = backoff_factor ** attempt
               time.sleep(wait_time)

**Graceful Degradation:**

.. code-block:: python

   def search_entities(self, query: str, **kwargs) -> Dict[str, Any]:
       """Search with graceful degradation."""
       try:
           # Try primary API
           return self._search_primary_api(query, **kwargs)
       except Exception as primary_error:
           try:
               # Fallback to secondary API
               return self._search_fallback_api(query, **kwargs)
           except Exception as fallback_error:
               # Return partial results if available
               return {
                   "status": "partial_success",
                   "data": [],
                   "metadata": {
                       "primary_error": str(primary_error),
                       "fallback_error": str(fallback_error),
                       "message": "Both APIs unavailable, returning cached results"
                   }
               }

Community and Support
=====================

Getting Help
------------

**Community Resources:**
- GitHub Discussions: General questions and feature discussions
- GitHub Issues: Bug reports and specific problems
- Email: Direct contact with maintainers
- Documentation: Comprehensive guides and examples

**Best Practices for Getting Help:**
1. Search existing issues first
2. Provide minimal reproducible examples
3. Include system information (Python version, OS, ToolUniverse version)
4. Share relevant error messages and tracebacks

Contributing Beyond Tools
-------------------------

**Other Ways to Contribute:**
- Improve documentation
- Add usage examples
- Fix bugs in existing tools
- Optimize performance
- Add new features to the core framework
- Help with testing and quality assurance

**Mentoring New Contributors:**
- Help newcomers understand the codebase
- Review pull requests from community members
- Create tutorials and learning materials
- Participate in community discussions

Recognition and Rewards
-----------------------

**Contributor Recognition:**
- Contributors are listed in release notes
- Major contributors get acknowledgment in documentation
- Annual contributor highlights
- Conference presentation opportunities for significant contributions

**Long-term Benefits:**
- Build your scientific software portfolio
- Gain experience with production-quality APIs
- Learn best practices for scientific data integration
- Network with other scientific developers

Conclusion
==========

Contributing to ToolUniverse is an opportunity to democratize access to scientific data and help build the next generation of AI scientist systems. By following this comprehensive Tutorial, you'll create high-quality tools that benefit the entire scientific community.

**Key Takeaways:**
1. **Quality First**: Focus on robust, well-tested, and well-documented tools
2. **User Experience**: Design intuitive APIs that scientists can easily use
3. **Community**: Engage with the community for feedback and support
4. **Continuous Improvement**: Maintain and improve your tools based on user feedback

**Next Steps:**
1. Choose a scientific data source you're passionate about
2. Follow this Tutorial step-by-step
3. Start with a simple tool and gradually add features
4. Engage with the community for feedback and support

Happy coding, and thank you for contributing to ToolUniverse! 🧬🔬🤖

---

**Additional Resources:**

- ToolUniverse GitHub: https://github.com/mims-harvard/ToolUniverse
- API Documentation: https://tooluniverse.readthedocs.io
- Community Discussions: https://github.com/mims-harvard/ToolUniverse/discussions
- Issue Tracker: https://github.com/mims-harvard/ToolUniverse/issues
