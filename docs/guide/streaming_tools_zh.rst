流式工具教程
==============

.. contents:: 目录
   :local:
   :depth: 2

什么是流式模式？
-----------------

流式（Streaming）指的是工具在任务执行过程中就把部分结果（“数据块”）推送给
调用方，而不是等到整个流程完全结束。它适用的场景包括：

* 输出内容较长，希望尽早看到整体方向
* 终端、MCP 客户端等界面想提供更好的实时体验
* 每个数据块都要进一步处理或记录（例如日志、前端渲染）

所有基于 :class:`AgenticTool` 的工具已经内建流式能力。其它工具可以参考
:ref:`zh-building-custom-streaming-tools` 自主扩展。

使用内置 Agentic 工具的流式功能
---------------------------------

ToolUniverse 中默认提供了大量 Agentic 工具，例如 ``ScientificTextSummarizer``
（定义在 ``agentic_tools.json``）。下面的示例演示如何通过
``ToolUniverse.run`` 搭配回调实现实时输出：

.. code-block:: python

   from tooluniverse.execute_function import ToolUniverse
   import json

   tu = ToolUniverse()
   tu.load_tools(include_tools=["ScientificTextSummarizer"])

   def on_chunk(text: str) -> None:
       print(text, end="", flush=True)

   fcall = json.dumps(
       {
           "name": "ScientificTextSummarizer",
           "arguments": {
               "text": "长篇论文……",
               "summary_length": "150",
               "focus_area": "conclusion",
           },
       }
   )

   result = tu.run(
       fcall,
       return_message=False,
       verbose=False,
       stream_callback=on_chunk,
   )

   print("\n最终结果:\n", result)

说明：

* ``stream_callback`` 告诉 ToolUniverse 调用方可以接收流式数据。
* ``ToolUniverse.run`` 接收的 JSON 结构与 MCP 调用一致。传入回调时，框架会
  自动在参数里补上工具声明的 ``STREAM_FLAG_KEY``（AgenticTool 的值是
  ``_tooluniverse_stream``），然后工具即可读取并开始输出数据块。
* 工具会依次调用回调输出数据块；没有回调时，则返回一次性结果。

仓库里的 ``examples/agentic_streaming_example.py`` 进一步展示了完整流程。

在 MCP / JSON 调用中开启流式输出
----------------------------------

当客户端无法传递 Python 回调时，可以在参数中显式开启旗标：

.. code-block:: json

   {
     "method": "tools/call",
     "params": {
       "name": "ScientificTextSummarizer",
       "arguments": {
         "text": "长篇论文……",
         "summary_length": "200",
         "focus_area": "methodology",
         "_tooluniverse_stream": true
       }
     }
   }

SMCP 服务器会将实时数据块转换为 ``ctx.info`` 日志通知，客户端即可获得实时输出。
最终汇总结果仍通过正常响应返回。

.. _zh-building-custom-streaming-tools:

自定义工具如何支持流式
------------------------

若要让自定义工具具备流式能力，请遵循以下步骤：

1. **在类上声明流式旗标名称**，用于和 ToolUniverse 协议。示例：

   .. code-block:: python

      class MyStreamingTool(BaseTool):
          STREAM_FLAG_KEY = "_tooluniverse_stream"

2. **在 ``run`` 方法中接受 ``stream_callback`` 并输出数据块**：

   .. code-block:: python

      from typing import Callable, Optional

      class MyStreamingTool(BaseTool):
          STREAM_FLAG_KEY = "_tooluniverse_stream"

          def run(
              self,
              arguments: dict,
              stream_callback: Optional[Callable[[str], None]] = None,
          ):
              arguments = dict(arguments)
              stream_enabled = bool(arguments.pop(self.STREAM_FLAG_KEY, False))

              if stream_enabled and stream_callback:
                  for chunk in self.generate_chunks(arguments):
                      stream_callback(chunk)
                  return "".join(self.generate_chunks(arguments))

              return self.run_without_streaming(arguments)

   请记得在无法流式输出时回退到一次性执行（例如抛出异常或直接返回完整结果）。

3. **（可选）在 schema 中列出该字段**，这样外部 JSON/MCP 调用也能显式开启流式。

测试
----

以下测试用例展示了流式行为，可作为实现或调试时的参考：

* ``tests/test_streaming_support.py`` – 覆盖回调注入与旗标处理的单元测试。
* ``tests/test_agentic_streaming_integration.py`` – 覆盖 AgenticTool 与 SMCP
  流式行为的集成测试。

运行方式：

.. code-block:: bash

   pytest tests/test_streaming_support.py tests/test_agentic_streaming_integration.py
