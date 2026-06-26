from typing import Generator

import anthropic
from anthropic.types import Message

from config import ANTHROPIC_API_KEY, DEFAULT_MODEL

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


# ---------------------------------------------------------------------------
# Message helpers
# ---------------------------------------------------------------------------

def add_user_message(messages: list, message) -> None:
    user_message = {
        "role": "user",
        "content": message.content if isinstance(message, Message) else message,
    }
    messages.append(user_message)


def add_assistant_message(messages: list, message) -> None:
    assistant_message = {
        "role": "assistant",
        "content": message.content if isinstance(message, Message) else message,
    }
    messages.append(assistant_message)


def text_from_message(message: Message) -> str:
    return "\n".join([block.text for block in message.content if block.type == "text"])


# ---------------------------------------------------------------------------
# Core chat function
# ---------------------------------------------------------------------------

def chat(
    messages: list,
    system=None,
    model: str = DEFAULT_MODEL,
    temperature: float = 1.0,
    stop_sequences: list[str] = [],
    tools: list | None = None,
    thinking: bool = False,
    thinking_budget: int = 1024,
    stream: bool = False,
) -> Message | Generator[str, None, None]:
    """
    Call the Claude API.

    Returns a full Message object (stream=False, default) or a generator that
    yields text chunks (stream=True). Always returns the full Message for non-
    streaming so that tool_use blocks are preserved.
    """
    params: dict = {
        "model": model,
        "max_tokens": 4000,
        "messages": messages,
        "temperature": temperature,
        "stop_sequences": stop_sequences,
    }
    if thinking:
        params["thinking"] = {"type": "enabled", "budget_tokens": thinking_budget}
    if tools:
        params["tools"] = tools
    if system:
        params["system"] = system

    if stream:
        return _stream_chat(params)

    return client.messages.create(**params)


def _stream_chat(params: dict) -> Generator[str, None, None]:
    with client.messages.stream(**params) as stream:
        for text in stream.text_stream:
            yield text


# ---------------------------------------------------------------------------
# Cache helpers — wrap system prompt and last tool schema with ephemeral cache
# ---------------------------------------------------------------------------

def with_cache(system_text: str) -> list[dict]:
    return [{"type": "text", "text": system_text, "cache_control": {"type": "ephemeral"}}]


def tools_with_cache(tools: list) -> list:
    if not tools:
        return tools
    return list(tools[:-1]) + [{**tools[-1], "cache_control": {"type": "ephemeral"}}]
