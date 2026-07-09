"""Sequential Thinking MCP 客户端 —— 管理 MCP 服务端生命周期，提供结构化推理能力"""
import asyncio
import json
import os
import subprocess
import sys
from typing import Optional


class SequentialThinkingClient:
    """MCP Sequential Thinking 客户端

    架构：
      本模块 ──JSON-RPC stdio──→ mcp-sequential-thinking (子进程)

    用于将复杂自然语言解析任务拆解为多步推理流程。
    """

    def __init__(self):
        self._session = None
        self._process = None
        self._stdio = None

    def start(self):
        """启动 MCP 服务端子进程"""
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        # 通过 uvx 或直接运行启动服务端
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "mcp_sequential_thinking.server"],
        )

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def _connect():
            self._stdio = stdio_client(server_params)
            read, write = await self._stdio.__aenter__()
            self._session = ClientSession(read, write)
            await self._session.__aenter__()
            await self._session.initialize()

        try:
            loop.run_until_complete(_connect())
        except Exception as e:
            print(f"[MCP] 服务端启动失败（尝试降级）: {e}")
            self._session = None

    def stop(self):
        """关闭 MCP 连接"""
        if self._session:
            try:
                loop = asyncio.get_event_loop()
                async def _close():
                    await self._session.__aexit__(None, None, None)
                    if self._stdio:
                        await self._stdio.__aexit__(None, None, None)
                loop.run_until_complete(_close())
            except Exception:
                pass
            self._session = None

    def process_thought(
        self,
        thought: str,
        thought_number: int,
        total_thoughts: int,
        next_thought_needed: bool,
        stage: str,
        tags: Optional[list] = None,
        is_revision: bool = False,
        revises_thought_number: Optional[int] = None,
        branch_from_thought: Optional[int] = None,
        branch_id: Optional[str] = None,
    ) -> dict:
        """记录一个推理步骤"""
        if not self._session:
            return {"error": "MCP 未连接"}

        args = {
            "thought": thought,
            "thought_number": thought_number,
            "total_thoughts": total_thoughts,
            "next_thought_needed": next_thought_needed,
            "stage": stage,
        }
        if tags:
            args["tags"] = tags
        if is_revision:
            args["is_revision"] = True
        if revises_thought_number is not None:
            args["revises_thought_number"] = revises_thought_number
        if branch_from_thought is not None:
            args["branch_from_thought"] = branch_from_thought
        if branch_id:
            args["branch_id"] = branch_id

        loop = asyncio.get_event_loop()
        async def _call():
            return await self._session.call_tool("process_thought", args)
        try:
            result = loop.run_until_complete(_call())
            return {"success": True, "content": str(result.content)}
        except Exception as e:
            return {"error": str(e)}

    def generate_summary(self) -> dict:
        """生成推理摘要"""
        if not self._session:
            return {"error": "MCP 未连接"}
        loop = asyncio.get_event_loop()
        async def _call():
            return await self._session.call_tool("generate_summary", {})
        try:
            result = loop.run_until_complete(_call())
            content = result.content[0].text if result.content else ""
            return {"success": True, "summary": json.loads(content) if content else {}}
        except Exception as e:
            return {"error": str(e)}

    def clear_history(self):
        """清空推理历史"""
        if not self._session:
            return
        loop = asyncio.get_event_loop()
        async def _call():
            return await self._session.call_tool("clear_history", {})
        try:
            loop.run_until_complete(_call())
        except Exception:
            pass
