"""The human-in-the-loop approval gate.

Agents are useful, but you rarely want them shipping to the world unsupervised. So the
pipeline ends at a **gate**: a human looks at the near-final draft and decides. This is
the "human-in-the-loop" pattern, and it's a hiring-manager favourite because it's what
separates a demo from something a company would actually run.

A gate is just a function: hand it the current state, it returns a decision. That shape
lets us swap behaviours without touching the orchestrator:

  auto_approve      always approves -- used in tests, CI, and the offline demo so the
                    run finishes on its own.
  make_cli_approver interactive: prints the draft and asks a real person y / n / r.
  make_scripted_approver  replays a fixed list of decisions -- handy for notebooks and
                    tests that want to SHOW a human rejecting a draft, deterministically.

A decision is `(action, note)` where action is "approve", "revise", or "reject". On
"revise", `note` is the feedback the Writer will use for another pass.
"""

from __future__ import annotations

from collections.abc import Callable

from .state import TeamState

# A gate is any function TeamState -> (action, note).
Approver = Callable[[TeamState], tuple[str, str]]


def auto_approve(state: TeamState) -> tuple[str, str]:
    """The non-interactive gate: rubber-stamp whatever the team produced."""
    return ("approve", "")


def make_scripted_approver(decisions: list[tuple[str, str]]) -> Approver:
    """A gate that returns each decision in turn -- great for demos and tests.

    e.g. make_scripted_approver([("revise", "make the intro punchier"), ("approve", "")])
    reproduces 'the human bounced it once, then approved' with no typing.
    """
    queue = list(decisions)

    def approver(state: TeamState) -> tuple[str, str]:
        if queue:
            return queue.pop(0)
        return ("approve", "")  # run out of scripted answers -> approve and finish

    return approver


def make_cli_approver(input_fn: Callable[[str], str] = input) -> Approver:
    """An interactive gate for the terminal: show the draft, ask the human to decide."""

    def approver(state: TeamState) -> tuple[str, str]:
        print("\n" + "=" * 70)
        print("HUMAN REVIEW -- the team thinks this is ready:")
        print("=" * 70)
        print(state.draft)
        print("=" * 70)
        choice = input_fn("Approve (a) / Revise (r) / Reject (x)? ").strip().lower()
        if choice.startswith("a"):
            return ("approve", "")
        if choice.startswith("r"):
            note = input_fn("What should the writer change? ").strip()
            return ("revise", note)
        return ("reject", "")

    return approver
