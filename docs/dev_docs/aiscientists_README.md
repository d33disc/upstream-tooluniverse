# MCP 教程目录

欢迎来到 ToolUniverse 的 Model Context Protocol (MCP) 教程！

## 教程列表

###  基础教程
- **[添加 MCP 工具](adding_mcp_tools.md)** - 完整指南：如何在 ToolUniverse 中集成 MCP 工具
 - MCP 工具类型概述（MCPClientTool、MCPAutoLoaderTool、MCPProxyTool）
 - 配置和使用指南
 - 高级配置选项
 - 故障排除和最佳实践

###  高级教程
- **[MCP 工具注册系统](mcp_tool_registration_zh.md)** - 将本地工具注册为 MCP 工具
 - 使用 `@register_mcp_tool` 装饰器
 - 自动启动 MCP 服务器
 - 在其他 ToolUniverse 实例中自动加载远程工具
 - 复用 SMCP 功能实现工具分享

###  English Tutorials
- **[Adding MCP Tools](adding_mcp_tools_en.md)** - Complete Tutorial: How to integrate MCP tools in ToolUniverse
- **[MCP Tool Registration System](mcp_tool_registration_en.md)** - Register local tools as MCP tools

## 快速开始

如果你是首次接触 MCP 工具，建议按以下顺序学习：

1.  **[添加 MCP 工具](adding_mcp_tools.md)** - 从这里开始！
2.  **[MCP 工具注册系统](mcp_tool_registration_zh.md)** - 学习如何将本地工具暴露为 MCP 服务

## 什么是 MCP？

Model Context Protocol (MCP) 是一个开放的协议，用于连接 AI 应用程序与外部工具和数据源。在 ToolUniverse 中，MCP 工具让你能够：

-  连接到远程 MCP 服务器
- ️ 自动发现和加载远程工具
-  访问远程资源和提示
-  快速扩展工具生态系统

## 工具类型速览

| 工具类型 | 用途 | 适用场景 |
|---------|------|----------|
| **MCPClientTool** | 通用 MCP 客户端 | 需要完整 MCP 功能 |
| **MCPAutoLoaderTool** | 自动工具发现器 | 批量集成工具集 |
| **MCPProxyTool** | 单工具智能体 | 透明工具转发 |

## 示例配置预览

### 快速自动加载器
```json
{
   "name": "mcp_auto_loader",
   "type": "MCPAutoLoaderTool",
   "server_url": "http://localhost:8000",
   "auto_register": true,
   "tool_prefix": "mcp_"
}
```

### 专用工具智能体
```json
{
   "name": "mcp_calculator",
   "type": "MCPProxyTool",
   "server_url": "http://localhost:8000",
   "target_tool_name": "calculator"
}
```

## 相关资源

-  [ToolUniverse 主文档](../../README.md)
-  [API 参考](../../api/)
-  [配置示例](../../../src/tooluniverse/data/)
-  [MCP 协议规范](https://spec.modelcontextprotocol.io/)

---

**准备好开始了吗？** 点击 [添加 MCP 工具](adding_mcp_tools.md) 开始你的 MCP 之旅！
