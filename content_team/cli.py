"""Run the content team from the terminal.

    python -m content_team "how sleep affects learning"
    python -m content_team "vector databases" --audience "junior developers"
    python -m content_team "remote work" --interactive     # you are the approval gate
    python -m content_team "llms explained" --real          # real model via LiteLLM

By default it runs OFFLINE (deterministic fake agents) and auto-approves at the end, so
it finishes on its own and prints the full run: the handoff log, the editor's verdicts,
and the final post. Add --interactive to sit in the human-review seat yourself.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .humanloop import auto_approve, make_cli_approver
from .llm import DEFAULT_MODEL
from .orchestrator import run_topic
from .state import TeamState


def _print_event(stage: str, state: TeamState) -> None:
    """Live progress: one line per stage as the team works."""
    if stage == "research":
        print(f"[researcher] gathered {len(state.research)} bullets")
    elif stage == "write":
        tag = f"revision {state.revision_count}" if state.revision_count else "first draft"
        print(f"[writer]     wrote the {tag}")
    elif stage == "edit":
        r = state.editor_report
        if r.is_approved:
            print("[editor]     APPROVED")
        else:
            print(f"[editor]     REVISE -> {'; '.join(r.issues)}")
    elif stage == "human_review":
        print("[human]      reviewing...")


def _print_report(state: TeamState) -> None:
    print("\n" + "=" * 70)
    print("HANDOFF LOG (how the team collaborated)")
    print("=" * 70)
    for h in state.log:
        note = f" -- {h.note}" if h.note else ""
        print(f"  {h.frm:>18}  ->  {h.to:<12}{note}")

    print("\n" + "=" * 70)
    print(f"RESULT: {state.status.upper()}  (after {state.revision_count} revision(s))")
    print("=" * 70)
    print(state.final or state.draft)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="A Researcher/Writer/Editor agent team that writes a blog post."
    )
    parser.add_argument("topic", help="what the post should be about")
    parser.add_argument("--audience", default="general readers")
    parser.add_argument("--tone", default="friendly and informative")
    parser.add_argument("--max-revisions", type=int, default=2)
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="you are the human approval gate (approve/revise/reject)",
    )
    parser.add_argument(
        "--real",
        action="store_true",
        help="use a real model via LiteLLM (needs an API key). Default is offline.",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help="model string for --real")
    parser.add_argument("--out", help="write the final post to this Markdown file")
    args = parser.parse_args(argv)

    approver = make_cli_approver() if args.interactive else auto_approve
    mode = "REAL model " + args.model if args.real else "OFFLINE fake agents"
    print(f"content team ({mode}) writing about: {args.topic!r}\n")

    state = run_topic(
        args.topic,
        audience=args.audience,
        tone=args.tone,
        max_revisions=args.max_revisions,
        offline=not args.real,
        model=args.model,
        approver=approver,
        on_event=_print_event,
    )

    _print_report(state)

    if args.out:
        Path(args.out).write_text(state.final or state.draft, encoding="utf-8")
        print(f"\n[wrote the post to {args.out}]")


if __name__ == "__main__":
    sys.exit(main())
