"""
MCP client for connecting to the ComplianceWatch MCP server.

Usage:
    async with MCPClient("uv", ["run", "mcp_server/server.py"]) as client:
        tools = await client.list_tools()
        result = await client.call_tool("consultar_fornecedor", {"supplier_id": "SUP-001"})
"""
import json
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pydantic import AnyUrl


class MCPClient:
    def __init__(self, command: str, args: list[str], env: dict | None = None):
        self._command = command
        self._args = args
        self._env = env
        self._session: ClientSession | None = None
        self._exit_stack = AsyncExitStack()

    async def connect(self) -> None:
        params = StdioServerParameters(
            command=self._command,
            args=self._args,
            env=self._env,
        )
        stdio, write = await self._exit_stack.enter_async_context(stdio_client(params))
        self._session = await self._exit_stack.enter_async_context(
            ClientSession(stdio, write)
        )
        await self._session.initialize()

    async def list_tools(self) -> list:
        return (await self._session.list_tools()).tools

    async def call_tool(self, tool_name: str, tool_input: dict):
        return await self._session.call_tool(tool_name, tool_input)

    async def read_resource(self, uri: str):
        result = await self._session.read_resource(AnyUrl(uri))
        resource = result.contents[0]
        if resource.mimeType == "application/json":
            return json.loads(resource.text)
        return resource.text

    async def list_prompts(self) -> list:
        return (await self._session.list_prompts()).prompts

    async def get_prompt(self, prompt_name: str, args: dict) -> list:
        return (await self._session.get_prompt(prompt_name, args)).messages

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *_):
        await self._exit_stack.aclose()
