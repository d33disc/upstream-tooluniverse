# ToolUniverse

ToolUniverse is a collection of biomedical tools designed for use by Agentic AI.

# Install

### Local install

```
python -m pip install . --no-cache-dir
```

### Install from PIP

```
pip install tooluniverse
```

### Usage

Get all tools

```
from tooluniverse import ToolUniverse
tooluni = ToolUniverse()
tooluni.load_tools()
tool_name_list, tool_desc_list = tooluni.refresh_tool_name_desc()
print(tool_name_list)
print(tool_desc_list)
```

Function call to a tool

```
from tooluniverse import ToolUniverse
tooluni = ToolUniverse()
tooluni.load_tools()
tooluni.refresh_tool_name_desc()
query = {"name": "get_indications_by_drug_name", "arguments": {"drug_name": "KISUNLA"}}
tooluni.run(query)
```