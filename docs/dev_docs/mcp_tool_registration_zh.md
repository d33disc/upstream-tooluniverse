# MCP Tool Registration Tutorial - 将本地工具注册为 MCP 工具

本教程展示如何使用 ToolUniverse 的新功能，将本地工具注册为 MCP 工具，然后在另一个服务器上自动加载它们。

## 核心概念

### 问题
- 你有一个有用的本地工具
- 想要将它暴露给其他 ToolUniverse 实例使用
- 希望通过 MCP 协议实现远程访问

### 解决方案
1. 使用 `@register_mcp_tool` 装饰器注册本地工具
2. 启动 MCP 服务器暴露这些工具
3. 在其他 ToolUniverse 实例中使用 `load_mcp_tools()` 自动加载

## 快速开始

### 1. 服务器端 - 注册并暴露工具

```python
# my_analysis_server.py
from tooluniverse.mcp_tool_registry import register_mcp_tool, start_mcp_server

@register_mcp_tool(
   tool_type_name="protein_analyzer",
   config={
       "description": "分析蛋白质序列并返回详细信息",
       "parameter_schema": {
           "type": "object",
           "properties": {
               "sequence": {"type": "string", "description": "蛋白质序列"},
               "analysis_type": {"type": "string", "enum": ["basic", "detailed"], "default": "basic"}
           },
           "required": ["sequence"]
       }
   },
   mcp_config={
       "server_name": "Protein Analysis Server",
       "port": 8001,
       "host": "0.0.0.0"  # 允许远程访问
   }
)
class ProteinAnalyzer:
   def __init__(self, tool_config=None):
       self.tool_config = tool_config

   def run(self, arguments):
       sequence = arguments.get('sequence', '')
       analysis_type = arguments.get('analysis_type', 'basic')

       # 蛋白质分析逻辑
       result = {
           "sequence_length": len(sequence),
           "molecular_weight": len(sequence) * 110,  # 简化计算
           "analysis_type": analysis_type,
           "success": True
       }

       if analysis_type == "detailed":
           result.update({
               "amino_acid_composition": self._analyze_composition(sequence),
               "hydrophobicity": self._calculate_hydrophobicity(sequence)
           })

       return result

   def _analyze_composition(self, sequence):
       # 氨基酸组成分析
       composition = {}
       for aa in sequence:
           composition[aa] = composition.get(aa, 0) + 1
       return composition

   def _calculate_hydrophobicity(self, sequence):
       # 疏水性计算（简化版）
       hydrophobic = 'AILMFWYV'
       hydrophobic_count = sum(1 for aa in sequence if aa in hydrophobic)
       return hydrophobic_count / len(sequence) if sequence else 0

# 启动 MCP 服务器
if __name__ == "__main__":
   print("🚀 Starting Protein Analysis MCP Server...")
   start_mcp_server()  # 启动所有注册工具的服务器
   print("✅ Server running on http://localhost:8001")
```

### 2. 客户端 - 自动加载并使用远程工具

```python
# my_analysis_client.py
from tooluniverse import ToolUniverse

# 创建 ToolUniverse 实例
tu = ToolUniverse()

# 自动发现并加载 MCP 工具
print("🔄 Loading MCP tools from remote server...")
result = tu.load_mcp_tools(["http://localhost:8001"])

print(f"✅ Loaded {result['total_tools']} tools from {result['servers_connected']} servers")

# 使用远程蛋白质分析工具
protein_result = tu.tools.mcp_protein_analyzer(
   operation="call_tool",
   tool_name="protein_analyzer",
   tool_arguments={
       "sequence": "MKWVTFISLLFLFSSAYSRGVFRRDAHKSEVAHRFKDLGEENFKALVLIAFAQYLQQCPFEDHVKLVNEVTEFAKTCVADESAENCDKSLHTLFGDKLCTVATLRETYGEMADCCAKQEPERNECFLQHKDDNPNLPRLVRPEVDVMCTAFHDNEETFLKKYLYEIARRHPYFYAPELLFFAKRYKAAFTECCQAADKAACLLPKLDELRDEGKASSAKQRLKCASLQKFGERAFKAWAVARLSQRFPKAEFAEVSKLVTDLTKVHTECCHGDLLECADDRADLAKYICENQDSISSKLKECCEKPLLEKSHCIAEVENDEMPADLPSLAADFVESKDVCKNYAEAKDVFLGMFLYEYARRHPDYSVVLLLRLAKTYETTLEKCCAAADPHECYAKVFDEFKPLVEEPQNLIKQNCELFEQLGEYKFQNALLVRYTKKVPQVSTPTLVEVSRNLGKVGSKCCKHPEAKRMPCAEDYLSVVLNQLCVLHEKTPVSDRVTKCCTESLVNRRPCFSALEVDETYVPKEFNAETFTFHADICTLSEKERQIKKQTALVELVKHKPKATKEQLKAVMDDFAAFVEKCCKADDKETCFAEEGKKLVAASQAALGL",
       "analysis_type": "detailed"
   }
})

print("🧬 Protein Analysis Result:")
print(protein_result)

# 列出当前的 MCP 连接
connections = tu.list_mcp_connections()
print(f"\n🔗 Active MCP connections: {connections['total_mcp_tools']} tools")
print(f"📡 Connected servers: {connections['servers']}")
```

## 完整使用示例

### 1. 多工具服务器

```python
# multi_tool_server.py
from tooluniverse import register_mcp_tool, start_mcp_server

# 文本分析工具
@register_mcp_tool(
   name="text_sentiment",
   description="分析文本情感倾向",
   mcp_config={"port": 8001}
)
class TextSentimentTool:
   def run(self, arguments):
       text = arguments.get('text', '')

       # 简单情感分析
       positive_words = ['好', '棒', '优秀', '很好', 'amazing', 'great', 'excellent']
       negative_words = ['坏', '差', '糟糕', '不好', 'bad', 'terrible', 'awful']

       positive_count = sum(1 for word in positive_words if word in text.lower())
       negative_count = sum(1 for word in negative_words if word in text.lower())

       if positive_count > negative_count:
           sentiment = "positive"
       elif negative_count > positive_count:
           sentiment = "negative"
       else:
           sentiment = "neutral"

       return {
           "sentiment": sentiment,
           "confidence": abs(positive_count - negative_count) / max(1, positive_count + negative_count),
           "positive_indicators": positive_count,
           "negative_indicators": negative_count,
           "success": True
       }

# 数据统计工具
@register_mcp_tool(
   name="data_stats",
   description="计算数据统计指标",
   mcp_config={"port": 8001}  # 同一端口，同一服务器
)
class DataStatsTool:
   def run(self, arguments):
       data = arguments.get('data', [])
       if not data:
           return {"error": "数据不能为空", "success": False}

       return {
           "count": len(data),
           "sum": sum(data),
           "average": sum(data) / len(data),
           "min": min(data),
           "max": max(data),
           "range": max(data) - min(data),
           "success": True
       }

# 文件信息工具
@register_mcp_tool(
   name="file_analyzer",
   description="分析文件信息",
   mcp_config={"port": 8002}  # 不同端口，独立服务器
)
class FileAnalyzerTool:
   def run(self, arguments):
       import os
       from pathlib import Path

       filepath = arguments.get('filepath', '')
       if not filepath or not os.path.exists(filepath):
           return {"error": "文件不存在", "success": False}

       path = Path(filepath)
       stat = path.stat()

       return {
           "filename": path.name,
           "size_bytes": stat.st_size,
           "size_kb": round(stat.st_size / 1024, 2),
           "extension": path.suffix,
           "is_file": path.is_file(),
           "is_directory": path.is_dir(),
           "absolute_path": str(path.absolute()),
           "success": True
       }

if __name__ == "__main__":
   print("🚀 Starting Multi-Tool MCP Server...")

   # 列出注册的工具
   from tooluniverse import list_mcp_tools
   list_mcp_tools()

   # 启动所有服务器
   start_mcp_server()
   print("✅ Servers started!")
   print("   - Text & Data tools: http://localhost:8001")
   print("   - File tools: http://localhost:8002")
```

### 2. 智能客户端使用

```python
# smart_client.py
from tooluniverse import ToolUniverse

def main():
   tu = ToolUniverse()

   # 1. 先发现可用工具
   print("🔍 Discovering available MCP tools...")
   discovery = tu.discover_mcp_tools([
       "http://localhost:8001",
       "http://localhost:8002"
   ])

   print(f"Found {discovery['total_tools']} tools across {len(discovery['servers'])} servers:")
   for server, info in discovery['servers'].items():
       print(f"  📡 {server}: {info['count']} tools")
       for tool in info.get('tools', []):
           print(f"    - {tool['name']}: {tool['description']}")

   # 2. 加载所有工具
   print("\n🔄 Loading MCP tools...")
   load_result = tu.load_mcp_tools([
       "http://localhost:8001",
       "http://localhost:8002"
   ])

   print(f"✅ Loaded {load_result['total_tools']} tools")

   # 3. 使用工具进行分析
   print("\n🧪 Testing tools...")

   # 文本情感分析
   sentiment_result = tu.tools.mcp_text_sentiment(
       operation="call_tool",
       tool_name="text_sentiment",
       tool_arguments={
           "text": "这个工具真的很棒！它的功能amazing，我觉得很好用。"
       }
   })
   print(f"📝 Sentiment Analysis: {sentiment_result}")

   # 数据统计
   stats_result = tu.tools.mcp_data_stats(
       operation="call_tool",
       tool_name="data_stats",
       tool_arguments={
           "data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
       }
   })
   print(f"📊 Data Statistics: {stats_result}")

   # 文件分析
   file_result = tu.tools.mcp_file_analyzer(
       operation="call_tool",
       tool_name="file_analyzer",
       tool_arguments={
           "filepath": __file__  # 分析当前文件
       }
   })
   print(f"📁 File Analysis: {file_result}")

   # 4. 显示连接状态
   print("\n🔗 Connection Status:")
   connections = tu.list_mcp_connections()
   print(f"Total MCP tools loaded: {connections['total_mcp_tools']}")
   print(f"Active servers: {len(connections['servers'])}")
   for server in connections['servers']:
       print(f"  - {server}")

if __name__ == "__main__":
   main()
```

## 高级配置

### 1. 自定义参数 Schema

```python
@register_mcp_tool(
   name="advanced_analyzer",
   description="高级数据分析工具",
   parameter_schema={
       "type": "object",
       "properties": {
           "data": {
               "type": "array",
               "items": {"type": "number"},
               "description": "数值数据数组"
           },
           "analysis_config": {
               "type": "object",
               "properties": {
                   "method": {"type": "string", "enum": ["linear", "polynomial", "exponential"]},
                   "confidence_level": {"type": "number", "minimum": 0.8, "maximum": 0.99},
                   "include_plots": {"type": "boolean", "default": False}
               },
               "required": ["method"]
           },
           "output_format": {
               "type": "string",
               "enum": ["json", "csv", "xml"],
               "default": "json"
           }
       },
       "required": ["data", "analysis_config"]
   },
   mcp_config={
       "server_name": "Advanced Analytics Server",
       "port": 9000,
       "max_workers": 10  # 支持更多并发
   }
)
class AdvancedAnalyzer:
   def run(self, arguments):
       # 复杂分析逻辑
       pass
```

### 2. 生产环境配置

```python
# production_server.py
@register_mcp_tool(
   name="production_tool",
   description="生产环境工具",
   mcp_config={
       "server_name": "Production Analysis Service",
       "host": "0.0.0.0",  # 监听所有接口
       "port": 8080,
       "transport": "http",
       "max_workers": 20,  # 高并发支持
       "timeout": 300      # 5分钟超时
   }
)
class ProductionTool:
   def __init__(self, tool_config=None):
       # 生产环境初始化
       self.setup_logging()
       self.validate_environment()

   def run(self, arguments):
       # 生产级错误处理
       try:
           result = self.process_data(arguments)
           self.log_success(result)
           return result
       except Exception as e:
           self.log_error(e)
           return {"error": str(e), "success": False}
```

### 3. 批量注册现有工具

```python
# batch_registration.py
from tooluniverse import register_mcp_tool_from_config

# 现有工具类
class ExistingAnalysisTool:
   def run(self, arguments):
       return {"analysis": "completed"}

class ExistingProcessorTool:
   def run(self, arguments):
       return {"processing": "done"}

# 批量注册为 MCP 工具
tools_to_register = [
   {
       "class": ExistingAnalysisTool,
       "config": {
           "name": "analysis_tool",
           "description": "现有分析工具",
           "mcp_config": {"port": 8001}
       }
   },
   {
       "class": ExistingProcessorTool,
       "config": {
           "name": "processor_tool",
           "description": "现有处理工具",
           "mcp_config": {"port": 8001}
       }
   }
]

for tool_info in tools_to_register:
   register_mcp_tool_from_config(tool_info["class"], tool_info["config"])

# 启动服务器
from tooluniverse import start_mcp_server
start_mcp_server()
```

## 最佳实践

### 1. 错误处理
```python
def run(self, arguments):
   try:
       # 验证输入
       if not self.validate_input(arguments):
           return {"error": "输入验证失败", "success": False}

       # 执行逻辑
       result = self.process(arguments)

       # 返回结构化结果
       return {"result": result, "success": True}

   except ValueError as e:
       return {"error": f"参数错误: {str(e)}", "success": False}
   except Exception as e:
       return {"error": f"处理失败: {str(e)}", "success": False}
```

### 2. 性能优化
```python
# 使用连接池和缓存
@register_mcp_tool(
   name="optimized_tool",
   mcp_config={
       "max_workers": 10,  # 并发处理
       "timeout": 60       # 合理超时
   }
)
class OptimizedTool:
   def __init__(self, tool_config=None):
       self.cache = {}
       self.connection_pool = self.setup_pool()

   def run(self, arguments):
       # 缓存检查
       cache_key = self.get_cache_key(arguments)
       if cache_key in self.cache:
           return self.cache[cache_key]

       # 处理和缓存
       result = self.process(arguments)
       self.cache[cache_key] = result
       return result
```

### 3. 安全考虑
```python
@register_mcp_tool(
   name="secure_tool",
   mcp_config={
       "host": "127.0.0.1",  # 仅本地访问
       "port": 8001
   }
)
class SecureTool:
   def run(self, arguments):
       # 输入清理和验证
       clean_input = self.sanitize_input(arguments)

       # 权限检查
       if not self.check_permissions(clean_input):
           return {"error": "权限不足", "success": False}

       # 安全处理
       return self.secure_process(clean_input)
```

## 故障排除

### 常见问题

1. **服务器启动失败**
  ```python
  # 检查端口占用
  import socket
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  result = sock.connect_ex(('localhost', 8001))
  if result == 0:
      print("端口 8001 已被占用")
  ```

2. **工具不能被发现**
  ```python
  # 检查工具注册
  from tooluniverse import get_mcp_tool_registry
  registry = get_mcp_tool_registry()
  print("已注册的 MCP 工具:", list(registry.keys()))
  ```

3. **连接超时**
  ```python
  # 增加超时时间
  tu.load_mcp_tools(["http://localhost:8001"], timeout=60)
  ```

## 总结

通过这个 MCP 工具注册系统，你可以：

1.  **简单注册** - 使用 `@register_mcp_tool` 装饰器
2.  **自动暴露** - 一键启动 MCP 服务器
3.  **无缝集成** - 其他 ToolUniverse 实例自动发现和加载
4.  **复用 SMCP** - 完全基于现有的 SMCP 架构
5.  **生产就绪** - 支持并发、错误处理、配置管理

这样你就可以轻松地将有用的本地工具分享给团队的其他成员，或者在不同的服务器之间复用工具功能！
