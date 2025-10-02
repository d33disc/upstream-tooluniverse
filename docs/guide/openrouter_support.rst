OpenRouter Support
==================

ToolUniverse now includes full support for OpenRouter, allowing you to access a wide variety of LLM models from multiple providers through a single, unified API.

Overview
--------

OpenRouter provides access to models from:

* **OpenAI** (GPT-4o, O1, O3-mini)
* **Anthropic** (Claude 3.7 Sonnet, Claude 3.5 Sonnet, Claude 3 Opus/Haiku)
* **Google** (Gemini 2.0 Flash, Gemini Pro 1.5, Gemini Flash 1.5)
* **Alibaba** (Qwen 2.5, QwQ-32B)
* **DeepSeek** (DeepSeek Chat, DeepSeek R1)
* **Meta** (Llama 3.3, Llama 3.1)
* **Mistral** (Mistral Large, Pixtral Large)
* And many more!

Configuration
-------------

Environment Variables
^^^^^^^^^^^^^^^^^^^^^

To use OpenRouter, set the following environment variables:

.. code-block:: bash

    # Required
    export OPENROUTER_API_KEY="your_openrouter_api_key_here"
    
    # Optional - for usage tracking and attribution
    export OPENROUTER_SITE_URL="https://your-site.com"
    export OPENROUTER_SITE_NAME="Your Application Name"

Getting an API Key
^^^^^^^^^^^^^^^^^^

1. Visit `OpenRouter <https://openrouter.ai/>`_
2. Sign up for an account
3. Navigate to the API Keys section
4. Generate a new API key
5. Copy and set it as the ``OPENROUTER_API_KEY`` environment variable

Using OpenRouter with AgenticTool
----------------------------------

Basic Configuration
^^^^^^^^^^^^^^^^^^^

Configure an AgenticTool to use OpenRouter:

.. code-block:: python

    from tooluniverse import ToolUniverse
    
    # Example tool configuration using OpenRouter
    tool_config = {
        "name": "OpenRouter_Summarizer",
        "description": "Summarize text using OpenRouter models",
        "type": "AgenticTool",
        "prompt": "Summarize the following text:\n{text}",
        "input_arguments": ["text"],
        "parameter": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to summarize",
                    "required": True
                }
            },
            "required": ["text"]
        },
        "configs": {
            "api_type": "OPENROUTER",
            "model_id": "openai/gpt-4o",
            "temperature": 0.7,
            "return_json": False
        }
    }
    
    # Initialize ToolUniverse and register the tool
    tu = ToolUniverse()
    tu.register_tool_from_config(tool_config)
    
    # Use the tool
    result = tu.execute_tool("OpenRouter_Summarizer", {
        "text": "Your long text here..."
    })

Available Models
^^^^^^^^^^^^^^^^

OpenAI Models
"""""""""""""

.. list-table::
   :header-rows: 1
   :widths: 40 20 20 20

   * - Model ID
     - Max Output
     - Context Window
     - Best For
   * - ``openai/gpt-4o``
     - 64,000
     - 1,048,576
     - General purpose, multimodal
   * - ``openai/gpt-4o-mini``
     - 16,384
     - 128,000
     - Fast, cost-effective
   * - ``openai/o1``
     - 100,000
     - 200,000
     - Reasoning tasks
   * - ``openai/o3-mini``
     - 100,000
     - 200,000
     - Fast reasoning

Anthropic Models
""""""""""""""""

.. list-table::
   :header-rows: 1
   :widths: 40 20 20 20

   * - Model ID
     - Max Output
     - Context Window
     - Best For
   * - ``anthropic/claude-3.7-sonnet``
     - 8,192
     - 200,000
     - Latest, most capable
   * - ``anthropic/claude-3.5-sonnet``
     - 8,192
     - 200,000
     - Balanced performance
   * - ``anthropic/claude-3-opus``
     - 4,096
     - 200,000
     - Complex tasks
   * - ``anthropic/claude-3-haiku``
     - 4,096
     - 200,000
     - Fast, efficient

Google Models
"""""""""""""

.. list-table::
   :header-rows: 1
   :widths: 40 20 20 20

   * - Model ID
     - Max Output
     - Context Window
     - Best For
   * - ``google/gemini-2.0-flash-exp``
     - 8,192
     - 1,048,576
     - Latest experimental
   * - ``google/gemini-pro-1.5``
     - 8,192
     - 2,097,152
     - Large context
   * - ``google/gemini-flash-1.5``
     - 8,192
     - 1,048,576
     - Fast, cost-effective

Qwen Models
"""""""""""

.. list-table::
   :header-rows: 1
   :widths: 40 20 20 20

   * - Model ID
     - Max Output
     - Context Window
     - Best For
   * - ``qwen/qwq-32b-preview``
     - 8,192
     - 32,768
     - Reasoning preview
   * - ``qwen/qwen-2.5-72b-instruct``
     - 8,192
     - 131,072
     - General purpose
   * - ``qwen/qwen-2.5-coder-32b-instruct``
     - 8,192
     - 131,072
     - Code generation

Using OpenRouter with ToolFinderLLM
------------------------------------

Configure ToolFinderLLM to use OpenRouter models:

.. code-block:: python

    from tooluniverse import ToolUniverse
    
    # Create ToolUniverse instance
    tu = ToolUniverse()
    
    # Configure ToolFinderLLM with OpenRouter
    tool_finder_config = {
        "type": "ToolFinderLLM",
        "name": "Tool_Finder_OpenRouter",
        "description": "Find tools using OpenRouter LLMs",
        "configs": {
            "api_type": "OPENROUTER",
            "model_id": "anthropic/claude-3.5-sonnet",
            "temperature": 0.1,
            "max_new_tokens": 4096,
            "return_json": True,
            "exclude_tools": ["Tool_RAG", "Tool_Finder", "Finish"]
        }
    }
    
    # Register and use
    tu.register_tool_from_config(tool_finder_config)
    result = tu.execute_tool("Tool_Finder_OpenRouter", {
        "description": "tools for protein analysis",
        "limit": 5
    })

Fallback Configuration
----------------------

OpenRouter is included in the default fallback chain. If the primary API fails, the system will automatically try OpenRouter:

.. code-block:: python

    # Default fallback chain (in order):
    # 1. CHATGPT (Azure OpenAI)
    # 2. OPENROUTER (with openai/gpt-4o)
    # 3. GEMINI (Google Gemini)
    
    # You can customize the fallback chain with environment variable:
    import os
    import json
    
    custom_chain = [
        {"api_type": "OPENROUTER", "model_id": "anthropic/claude-3.5-sonnet"},
        {"api_type": "OPENROUTER", "model_id": "openai/gpt-4o"},
        {"api_type": "GEMINI", "model_id": "gemini-2.0-flash"}
    ]
    
    os.environ["AGENTIC_TOOL_FALLBACK_CHAIN"] = json.dumps(custom_chain)

Advanced Configuration
----------------------

Custom Model Limits
^^^^^^^^^^^^^^^^^^^

Override default token limits for specific models:

.. code-block:: python

    import os
    import json
    
    custom_limits = {
        "openai/gpt-4o": {
            "max_output": 32000,  # Custom limit
            "context_window": 1048576
        },
        "anthropic/claude-3.7-sonnet": {
            "max_output": 4096,
            "context_window": 200000
        }
    }
    
    os.environ["OPENROUTER_DEFAULT_MODEL_LIMITS"] = json.dumps(custom_limits)

Per-Model Max Tokens
^^^^^^^^^^^^^^^^^^^^

Set specific max_tokens for individual models:

.. code-block:: python

    import os
    import json
    
    max_tokens_config = {
        "openai/gpt-4o": 16000,
        "anthropic/claude-3.5-sonnet": 4096,
        "google/gemini-2.0-flash-exp": 8192
    }
    
    os.environ["OPENROUTER_MAX_TOKENS_BY_MODEL"] = json.dumps(max_tokens_config)

Complete Example
----------------

Here's a complete example showing OpenRouter usage in a scientific workflow:

.. code-block:: python

    import os
    from tooluniverse import ToolUniverse
    
    # Set up OpenRouter API key
    os.environ["OPENROUTER_API_KEY"] = "your_api_key_here"
    
    # Initialize ToolUniverse
    tu = ToolUniverse()
    
    # Create a tool for analyzing scientific papers
    paper_analyzer_config = {
        "name": "Paper_Analyzer",
        "description": "Analyze scientific papers and extract key findings",
        "type": "AgenticTool",
        "prompt": """Analyze this scientific paper abstract and extract:
    1. Main research question
    2. Methodology used
    3. Key findings
    4. Implications
    
    Abstract: {abstract}
    
    Provide a structured analysis.""",
        "input_arguments": ["abstract"],
        "parameter": {
            "type": "object",
            "properties": {
                "abstract": {
                    "type": "string",
                    "description": "Scientific paper abstract",
                    "required": True
                }
            },
            "required": ["abstract"]
        },
        "configs": {
            "api_type": "OPENROUTER",
            "model_id": "anthropic/claude-3.5-sonnet",
            "temperature": 0.3,
            "return_json": False
        }
    }
    
    # Register the tool
    tu.register_tool_from_config(paper_analyzer_config)
    
    # Use the tool
    abstract = """
    Recent advances in deep learning have enabled accurate protein structure 
    prediction from amino acid sequences...
    """
    
    result = tu.execute_tool("Paper_Analyzer", {"abstract": abstract})
    print(result)

Best Practices
--------------

1. **Choose the Right Model**: Select models based on your task requirements:
   
   * Use GPT-4o for general-purpose tasks with multimodal capabilities
   * Use Claude 3.5/3.7 Sonnet for complex reasoning and analysis
   * Use Gemini 2.0 Flash for tasks requiring very large context windows
   * Use Qwen models for specialized tasks or cost optimization

2. **Set Appropriate Parameters**:
   
   * Use lower temperature (0.1-0.3) for factual, deterministic outputs
   * Use higher temperature (0.7-1.0) for creative tasks
   * Set max_tokens based on expected output length

3. **Handle Fallbacks**: Configure fallback chains for reliability:
   
   .. code-block:: python
   
       tool_config = {
           # ... other config ...
           "configs": {
               "api_type": "OPENROUTER",
               "model_id": "anthropic/claude-3.5-sonnet",
               "fallback_api_type": "OPENROUTER",
               "fallback_model_id": "openai/gpt-4o",
               "use_global_fallback": True
           }
       }

4. **Monitor Costs**: Different models have different pricing. Check `OpenRouter's pricing page <https://openrouter.ai/pricing>`_ for current rates.

5. **Use Site Attribution**: Set ``OPENROUTER_SITE_URL`` and ``OPENROUTER_SITE_NAME`` for better tracking and potential discounts.

Troubleshooting
---------------

API Key Issues
^^^^^^^^^^^^^^

If you see ``OPENROUTER_API_KEY not set`` errors:

1. Verify the environment variable is set correctly
2. Check for typos in the variable name
3. Ensure the key has not expired
4. Verify the key has sufficient credits

Model Not Found
^^^^^^^^^^^^^^^

If a model is not available:

1. Check the model name format: ``provider/model-name``
2. Verify the model is available on OpenRouter
3. Check your account has access to the model
4. Try an alternative model from the same provider

Rate Limiting
^^^^^^^^^^^^^

OpenRouter implements rate limiting. If you hit limits:

1. The client will automatically retry with exponential backoff
2. Consider using a different model with higher rate limits
3. Upgrade your OpenRouter plan if needed

Support
-------

For OpenRouter-specific issues:

* Visit `OpenRouter Documentation <https://openrouter.ai/docs>`_
* Check `OpenRouter Discord <https://discord.gg/openrouter>`_

For ToolUniverse integration issues:

* Open an issue on the `ToolUniverse GitHub <https://github.com/your-repo/tooluniverse>`_
* Check the existing documentation and examples


