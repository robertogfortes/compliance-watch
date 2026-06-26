"""
Deep-investigation agent — the ONLY agentic component in ComplianceWatch.

This is NOT part of the automated pipeline. It is triggered MANUALLY by a compliance
analyst who wants to investigate a case that the pipeline already flagged.

Why this is an Agent (not a Workflow):
- The number of tool calls needed is unknown in advance.
- The analyst may ask follow-up questions mid-session.
- The agent decides whether to use extended thinking based on its own uncertainty.

See docs/architecture-decision.md for the full workflow-vs-agent rationale.

Entry point: python agent/investigacao_profunda.py --case <case_id>
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.claude_client import (
    add_assistant_message,
    add_user_message,
    chat,
    text_from_message,
    with_cache,
    tools_with_cache,
)
from core.run_tools import run_tools
from prompts.system_auditor import SYSTEM_AUDITOR
from tools.schemas import ALL_TOOL_SCHEMAS
from config import DEFAULT_MODEL, HIGH_RISK_MODEL, MAX_ANALYSIS_TEMPERATURE

_AGENT_SYSTEM = (
    SYSTEM_AUDITOR
    + "\n\n"
    "<agent_mode>\n"
    "You are now in deep-investigation mode for a flagged case. You have access to all "
    "compliance tools and may call them as many times as needed. When you need additional "
    "information from the analyst (e.g., the original contract date, a missing document), "
    "ASK the analyst directly rather than making assumptions. State clearly what you need "
    "and why. Only conclude the investigation when you have enough evidence to make a "
    "well-supported recommendation.\n"
    "</agent_mode>"
)

_CONFIDENCE_THRESHOLD_FOR_THINKING = 6


def _should_use_extended_thinking(confidence: float) -> bool:
    """Activate extended thinking only when the agent's confidence is low."""
    return confidence < _CONFIDENCE_THRESHOLD_FOR_THINKING


def investigate(
    case_summary: str,
    flagged_document: str,
    interactive: bool = True,
) -> list[dict]:
    """
    Run the deep-investigation agent loop.

    The loop:
    1. Claude analyses the case and calls tools as needed.
    2. If Claude asks the analyst a question (stop_reason == 'end_turn' with a question),
       the agent pauses for human input.
    3. Extended thinking is activated automatically when confidence drops below threshold.
    4. Loop ends when Claude produces a final recommendation without pending tool calls.

    Returns the full conversation message list (audit trail).
    """
    messages = []
    add_user_message(
        messages,
        f"A compliance anomaly has been flagged. Please investigate.\n\n"
        f"<case_summary>\n{case_summary}\n</case_summary>\n\n"
        f"<flagged_document>\n{flagged_document}\n</flagged_document>\n\n"
        "Begin your investigation. Use the available tools to gather evidence. "
        "If you need additional information from me (the analyst), ask clearly.",
    )

    current_confidence = 10.0
    turn = 0
    max_turns = 20

    while turn < max_turns:
        turn += 1
        use_thinking = _should_use_extended_thinking(current_confidence)

        response = chat(
            messages,
            system=with_cache(_AGENT_SYSTEM),
            tools=tools_with_cache(ALL_TOOL_SCHEMAS),
            model=HIGH_RISK_MODEL if use_thinking else DEFAULT_MODEL,
            temperature=0.0 if not use_thinking else MAX_ANALYSIS_TEMPERATURE,
            thinking=use_thinking,
            thinking_budget=4096,
        )
        add_assistant_message(messages, response)

        if response.stop_reason == "tool_use":
            tool_results = run_tools(response)
            add_user_message(messages, tool_results)
            continue

        # stop_reason == "end_turn" — Claude finished a turn
        response_text = text_from_message(response)

        # Heuristic: check if Claude is asking a question (ends with ?)
        last_sentence = response_text.strip().rsplit(".", 1)[-1].strip()
        is_question = "?" in last_sentence

        if interactive and is_question:
            print("\n[AGENT]\n" + response_text)
            print("\n[ANALYST INPUT REQUIRED] —", end=" ")
            analyst_input = input().strip()
            if analyst_input.lower() in ("done", "exit", "quit"):
                break
            add_user_message(messages, analyst_input)
            # Reduce confidence after analyst provided new info
            current_confidence = max(3.0, current_confidence - 1.5)
            continue

        # No more questions — investigation complete
        print("\n[AGENT FINAL REPORT]\n" + response_text)
        break

    return messages


def _run_cli():
    parser = argparse.ArgumentParser(
        description="Deep-investigation agent for a flagged compliance case."
    )
    parser.add_argument("--case", required=True, help="Path to case JSON or inline case summary")
    parser.add_argument("--document", default="", help="Path to flagged document text file")
    parser.add_argument("--no-interactive", action="store_true", help="Disable analyst prompts")
    args = parser.parse_args()

    if os.path.exists(args.case):
        with open(args.case, encoding="utf-8") as f:
            case_data = json.load(f)
        case_summary = case_data.get("case_summary", str(case_data))
    else:
        case_summary = args.case

    flagged_document = ""
    if args.document and os.path.exists(args.document):
        with open(args.document, encoding="utf-8") as f:
            flagged_document = f.read()

    print(f"Starting deep investigation...\nCase: {case_summary[:200]}\n")
    investigate(
        case_summary=case_summary,
        flagged_document=flagged_document,
        interactive=not args.no_interactive,
    )


if __name__ == "__main__":
    _run_cli()
