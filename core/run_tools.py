"""
Dispatch all tool_use blocks in a message and return tool_result blocks.

Errors are caught per-tool so one failing tool doesn't abort the others.
"""
import json

from anthropic.types import Message

from core.run_tool import run_tool


def run_tools(message: Message) -> list[dict]:
    tool_requests = [block for block in message.content if block.type == "tool_use"]
    tool_result_blocks = []

    for tool_request in tool_requests:
        try:
            tool_output = run_tool(tool_request.name, tool_request.input)
            tool_result_block = {
                "type": "tool_result",
                "tool_use_id": tool_request.id,
                "content": json.dumps(tool_output),
                "is_error": False,
            }
        except Exception as exc:
            tool_result_block = {
                "type": "tool_result",
                "tool_use_id": tool_request.id,
                "content": f"Error: {exc}",
                "is_error": True,
            }
        tool_result_blocks.append(tool_result_block)

    return tool_result_blocks
