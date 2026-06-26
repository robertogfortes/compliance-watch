"""Phase 0 smoke test — verifies that chat() and streaming work end-to-end."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.claude_client import (
    add_user_message,
    add_assistant_message,
    text_from_message,
    chat,
)
from config import HAIKU


def test_basic_call():
    messages = []
    add_user_message(messages, "Reply with exactly: OK")
    response = chat(messages, model=HAIKU, temperature=0.0)
    add_assistant_message(messages, response)
    text = text_from_message(response)
    assert "OK" in text, f"Unexpected response: {text}"
    print(f"[PASS] basic call: {text!r}")
    return response


def test_multi_turn():
    messages = []
    add_user_message(messages, "Remember the number 42.")
    r1 = chat(messages, model=HAIKU, temperature=0.0)
    add_assistant_message(messages, r1)
    add_user_message(messages, "What number did I ask you to remember?")
    r2 = chat(messages, model=HAIKU, temperature=0.0)
    text = text_from_message(r2)
    assert "42" in text, f"Multi-turn failed: {text!r}"
    print(f"[PASS] multi-turn: {text!r}")


def test_streaming():
    messages = []
    add_user_message(messages, "Count from 1 to 5, one number per line.")
    chunks = list(chat(messages, model=HAIKU, temperature=0.0, stream=True))
    full_text = "".join(chunks)
    assert len(chunks) > 1, "Expected multiple chunks from streaming"
    assert "1" in full_text and "5" in full_text, f"Streaming output unexpected: {full_text!r}"
    print(f"[PASS] streaming: received {len(chunks)} chunks")


if __name__ == "__main__":
    print("Running Phase 0 smoke tests...\n")
    test_basic_call()
    test_multi_turn()
    test_streaming()
    print("\nAll tests passed.")
