"""
Multi-turn conversation loop with tool use.

Canonical pattern: loop until stop_reason != "tool_use".
Never inline this logic at call sites.
"""
from anthropic.types import Message

from core.claude_client import add_assistant_message, add_user_message, chat
from core.run_tools import run_tools


def run_conversation(
    messages: list,
    tools: list | None = None,
    system=None,
    model: str | None = None,
    temperature: float = 0.2,
) -> list:
    """
    Drive a conversation until Claude stops requesting tools.

    Returns the updated messages list (same object, mutated in place).
    """
    kwargs = {"tools": tools or [], "system": system, "temperature": temperature}
    if model:
        kwargs["model"] = model

    while True:
        response: Message = chat(messages, **kwargs)
        add_assistant_message(messages, response)

        if response.stop_reason != "tool_use":
            break

        tool_results = run_tools(response)
        add_user_message(messages, tool_results)

    return messages
