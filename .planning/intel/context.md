# Context

## Agentic PO translation implementation
- source: docs/translation_tools/AGENTIC_TRANSLATION_TOOL_SUMMARY.md
- notes:
  DATA_2084fd34_START
  我们成功创建了一个基于 ToolUniverse AgenticTool 框架的翻译工具，用于批量翻译 .po 文件，**无需修改任何源代码**。这个解决方案完全在 `docs` 目录下实现，展示了如何利用 ToolUniverse 的 AgenticTool 功能来构建强大的翻译工具。
  DATA_2084fd34_END

## Adding tools quick reference
- source: docs/dev_docs/Adding_Tools_Quick_Reference.md
- notes:
  DATA_88f49529_START
  - [ ] File ends with `_tool.py`
  - [ ] Placed in `src/tooluniverse/`
  - [ ] Class has `__init__(self, tool_config=None)`
  - [ ] Class has `run(self, arguments)` method
  - [ ] Config has all required fields (`name`, `type`, `description`, `parameter`)
  - [ ] Returns consistent format (`success: True/False`)
  - [ ] Error handling implemented
  DATA_88f49529_END

## Adding tools tutorial
- source: docs/dev_docs/Adding_Tools_Tutorial.md
- notes:
  DATA_4646e9cb_START
  This tutorial covers everything you need to know about adding custom tools to ToolUniverse using the decorator-based auto-registration system.
  DATA_4646e9cb_END

## Documentation standards
- source: docs/dev_docs/DOCUMENTATION_STANDARDS.md
- notes:
  DATA_4a940ed1_START
  These rules keep ToolUniverse documentation accurate as the tool and skill
  catalogs change.
  DATA_4a940ed1_END

## Documentation structure
- source: docs/DOCUMENTATION_STRUCTURE.md
- notes:
  DATA_aef06785_START
  This document describes how the docs folder is organized to match the doctree (sidebar navigation).
  DATA_aef06785_END

## Embedding search
- source: docs/dev_docs/Embedding_Search.md
- notes:
  DATA_632c038b_START
  `find_tools` turns a natural-language request into a ranked list of tools. It
  embeds the query and compares it with cached embeddings of the tools currently
  loaded by `ToolUniverse`.
  DATA_632c038b_END

## Full-text access
- source: docs/dev_docs/FULLTEXT_ACCESS_GUIDE.md
- notes:
  DATA_fe7e4dee_START
  Literature search tools (PubMed, Europe PMC, OpenAlex, Semantic Scholar) intentionally return **metadata + abstract only**, not full text. This is by design:
  DATA_fe7e4dee_END

## Interaction surfaces
- source: docs/dev_docs/Interaction_Surfaces.md
- notes:
  DATA_97cb24ce_START
  How an outside codebase, agent, or human reaches into ToolUniverse and pulls
  information together iteratively.
  DATA_97cb24ce_END

## MCP server conversion
- source: docs/dev_docs/MCP_Server_Tutorial.md
- notes:
  DATA_158b4bc3_START
  This tutorial will Tutorial you through the process of converting your Python program into a Model Context Protocol (MCP) server and integrating it with ToolUniverse for easy access and management.
  DATA_158b4bc3_END

## MCP Tasks
- source: docs/MCP_TASKS_GUIDE.md
- notes:
  DATA_7812595f_START
  ToolUniverse now supports **MCP Tasks** ([Model Context Protocol Tasks](https://modelcontextprotocol.io/specification/2025-11-25/basic/utilities/tasks)), enabling non-blocking execution of long-running scientific operations. This native protocol support allows tools like ProteinsPlus docking (5-60 minutes) and SwissDock simulations (10-30 minutes) to run in the background while you continue working.
  DATA_7812595f_END

## ODPHP tools
- source: docs/dev_docs/ODPHPtools_tutorial.md
- notes:
  DATA_5a974415_START
  **What it is.** A fast, agent-aligned interface to the U.S. Office of Disease Prevention and Health Promotion (ODPHP) **MyHealthfinder API**:
  DATA_5a974415_END

## Translation tools
- source: docs/translation_tools/README.md
- notes:
  DATA_ed7d74a3_START
  这个文件夹包含了基于 ToolUniverse AgenticTool 的翻译工具，用于批量翻译 .po 文件。
  DATA_ed7d74a3_END

## bioRxiv and medRxiv search
- source: docs/dev_docs/SEARCHING_BIORXIV.md
- notes:
  DATA_ee2536f5_START
  The official bioRxiv API only supports **direct DOI/date-based retrieval**, not keyword/text search. This is a fundamental limitation of their public API.
  DATA_ee2536f5_END

## Test response structures
- source: docs/dev_docs/TEST_WRITING_GUIDE.md
- notes:
  DATA_d72c0e5a_START
  When writing tests for ToolUniverse tools, be aware that tool responses may have data in either a **flat** or **nested** structure depending on the tool implementation.
  DATA_d72c0e5a_END

## Tool Description Optimizer quick start
- source: docs/dev_docs/Tool_Description_Optimizer_Quick_Start.md
- notes:
  DATA_8ba58a6c_START
  Want to improve your tool descriptions in minutes? Here's how:
  DATA_8ba58a6c_END

## Tool Description Optimizer
- source: docs/dev_docs/Tool_Description_Optimizer_Tutorial.md
- notes:
  DATA_bffac41a_START
  The ToolDescriptionOptimizer is an AI-powered tool that automatically improves tool documentation through iterative optimization. It analyzes actual test results to generate more accurate, concise, and user-friendly descriptions.
  DATA_bffac41a_END

## Documentation utility scripts
- source: docs/dev_docs/UTILITY_SCRIPTS.md
- notes:
  DATA_f7d418cf_START
  This document provides a comprehensive guide to all utility scripts in the `docs/` directory.
  DATA_f7d418cf_END

## Documentation validation
- source: docs/dev_docs/VALIDATION_GUIDE.md
- notes:
  DATA_5d2dd056_START
  Run the smallest checks that cover the edited pages, then build the complete
  documentation when navigation, shared references, or generated content changes.
  DATA_5d2dd056_END

## Boltz2 remote tool
- source: docs/tools/remote/boltz.md
- notes:
  DATA_61be1d69_START
  This tutorial will Tutorial you through setting up and running MCP (Model Context Protocol) server-based tools for Boltz2 molecular docking.
  DATA_61be1d69_END

## DepMap gene correlation
- source: docs/tools/remote/depmap_24q2.md
- notes:
  DATA_5e20c335_START
  A MCP tool from [Prism ToolSpace](https://huggingface.co/datasets/mims-harvard/ToolSpace) for analyzing gene-gene correlations from the [DepMap (Dependency Map)](https://depmap.org/) CRISPR knockout screening dataset. This tool processes systematic CRISPR-Cas9 knockout data from over 1,320 cancer cell lines from DepMap 24Q2 to identify genetic dependencies and co-essential gene pairs.
  DATA_5e20c335_END

## Human expert feedback
- source: docs/tools/remote/expert_feedback.md
- notes:
  DATA_e3731f0f_START
  The Human Expert Feedback System is a sophisticated **human-in-the-loop** consultation platform designed for ToolUniverse. It enables AI systems to seamlessly consult with human experts when encountering complex decisions, particularly in medical and scientific domains where expert knowledge is crucial.
  DATA_e3731f0f_END
- source: docs/guide/expert_feedback.md
- notes:
  DATA_6da5ac48_START
  The Human Expert Feedback System is a sophisticated **human-in-the-loop** consultation platform designed for ToolUniverse. It enables AI systems to seamlessly consult with human experts when encountering complex decisions, particularly in medical and scientific domains where expert knowledge is crucial.
  DATA_6da5ac48_END

## COMPASS immunotherapy prediction
- source: docs/tools/remote/immune_compass.md
- notes:
  DATA_12793106_START
  A MCP tool from [Prism ToolSpace](https://huggingface.co/datasets/mims-harvard/ToolSpace) for running immune checkpoint inhibitor (ICI) response predictions using the [COMPASS model](https://github.com/mims-harvard/COMPASS). This tool processes the pateint level mRNA's TPM (transcripts per million) tumor expression profile and cancer context to predict patient responsiveness for immunotherapy and provides interpretable insights through immune cell concept analysis.
  DATA_12793106_END

## MCP tool registration tutorial
- source: docs/dev_docs/mcp_tool_registration_en.md
- notes:
  DATA_f7fa813b_START
  This tutorial demonstrates how to use ToolUniverse's new functionality to register local tools as MCP tools and automatically load them on other servers.
  DATA_f7fa813b_END

## PINNACLE embeddings
- source: docs/tools/remote/pinnacle.md
- notes:
  DATA_cb444799_START
  The [PINNACLE](https://github.com/mims-harvard/PINNACLE) tool provides access to cell-type-specific protein-protein interaction embeddings. These embeddings capture functional relationships between proteins in different cellular contexts, enabling advanced analysis for drug discovery, disease research, and systems biology.
  DATA_cb444799_END

## USPTO downloader
- source: docs/tools/remote/uspto_downloader.md
- notes:
  DATA_4683a91d_START
  This tutorial will Tutorial you through setting up and running MCP (Model Context Protocol) server-based tools for USPTO patent document downloading. This tool requires GPUs to run optical character recognition on the patent PDFs and extract the patent text.
  DATA_4683a91d_END
