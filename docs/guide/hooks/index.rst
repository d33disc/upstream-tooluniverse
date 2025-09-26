Post-processing Tool Outputs
============================

**Intelligent output processing for ToolUniverse**

The ToolUniverse Hooks system provides automatic post-processing of tool outputs. Use hooks to summarize long results, save large outputs to files, and customize behavior per tool or workflow.

.. toctree::
   :maxdepth: 1
   :caption: Hook Topics

   summarization_hook
   file_save_hook
   hook_configuration
   server_stdio_hooks

**Topic summaries**

- :doc:`summarization_hook`: Automatically condenses long tool outputs into concise, high-signal summaries. Useful for literature results, large datasets, and multi-step workflows.
- :doc:`file_save_hook`: Saves large outputs to disk with metadata for later processing and sharing. Ideal for heavy payloads, audit trails, and external pipelines.
- :doc:`hook_configuration`: Configure which hooks run, when they trigger, and how they behave. Supports thresholds, per-tool rules, and advanced options.
- :doc:`server_stdio_hooks`: How to use hooks in server (HTTP/SSE) and stdio modes. Covers CLI flags, Python API, defaults, and best practices.
