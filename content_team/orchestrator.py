"""The orchestrator -- the state machine that routes work between the agents.

This is the star of the project. The agents are just workers; the orchestrator is the
thing that decides *who goes next*, and that decision is the entire difference between
a toy and a system.

Model it as a state machine. Each state is a place the work can be; each arrow is a
rule for where it goes next:

        +-----------+     +-------+     +------+
        | RESEARCH  | --> | WRITE | --> | EDIT |
        +-----------+     +-------+     +------+
                             ^             |
                revise (<max)|             | verdict
                             |             v
                          +--+-------------+--+
                          |   HUMAN_REVIEW    |  approve --> DONE
                          +-------------------+  revise (<max) --> WRITE
                                                 reject  --> DONE (rejected)

Two things make it a real system and not a straight line:

  1. The EDIT -> WRITE loop. If the Editor says "revise", the draft goes BACK to the
     Writer with the Editor's notes. That's a cycle, and cycles need a stop condition --
     here, `max_revisions`. This is why you model agents as a state machine instead of
     a chain of function calls: chains can't loop safely.

  2. The HUMAN_REVIEW gate. A person can approve, bounce it back for another pass, or
     reject outright. Same loop, different reviewer.

Every transition is written to `state.log`, so afterwards you can read exactly how the
team collaborated -- who handed what to whom, and why.
"""

from __future__ import annotations

from collections.abc import Callable

from .agents import edit, research, write
from .humanloop import Approver, auto_approve
from .state import TeamState

# A tiny optional hook so a UI or the CLI can watch the run unfold: called with the
# name of the stage that just finished and the current state.
EventHook = Callable[[str, TeamState], None]


def _emit(hook: EventHook | None, stage: str, state: TeamState) -> None:
    if hook is not None:
        hook(stage, state)


def run_team(
    state: TeamState,
    *,
    offline: bool = True,
    model: str | None = None,
    approver: Approver | None = None,
    on_event: EventHook | None = None,
) -> TeamState:
    """Run the whole team on `state` until the post is approved or rejected.

    `approver` is the human gate (defaults to auto-approve so it finishes on its own).
    `on_event` is an optional callback fired after each stage, for live progress.
    Returns the same `state`, now filled in and with `status` set.
    """
    approver = approver or auto_approve
    current = "RESEARCH"

    while current != "DONE":
        if current == "RESEARCH":
            state.research = research(state, offline=offline, model=model)
            state.record("orchestrator", "researcher", "gather facts")
            state.record("researcher", "writer", f"{len(state.research)} bullets")
            _emit(on_event, "research", state)
            current = "WRITE"

        elif current == "WRITE":
            state.draft = write(state, offline=offline, model=model)
            who = "writer (revision)" if state.revision_count else "writer"
            state.record(who, "editor", "draft ready for review")
            _emit(on_event, "write", state)
            current = "EDIT"

        elif current == "EDIT":
            report = edit(state.draft, offline=offline, model=model)
            state.editor_report = report
            _emit(on_event, "edit", state)
            if not report.is_approved and state.revision_count < state.max_revisions:
                # Bounce it back to the Writer with the Editor's notes. This is the loop.
                state.revision_count += 1
                state.feedback = "; ".join(report.issues)
                state.record("editor", "writer", f"revise: {state.feedback}")
                current = "WRITE"
            else:
                # Editor approved, OR we've hit the revision cap -- either way, a human
                # decides next.
                note = "editor approved" if report.is_approved else "revision cap reached"
                state.record("editor", "human", note)
                current = "HUMAN_REVIEW"

        elif current == "HUMAN_REVIEW":
            action, feedback = approver(state)
            _emit(on_event, "human_review", state)
            if action == "approve":
                state.status = "approved"
                state.final = state.draft
                state.record("human", "orchestrator", "approved -- shipping")
                current = "DONE"
            elif action == "revise" and state.revision_count < state.max_revisions:
                state.revision_count += 1
                state.feedback = feedback or "address the reviewer's notes"
                state.record("human", "writer", f"revise: {state.feedback}")
                current = "WRITE"
            else:
                # Rejected, or the human wanted another pass but we're out of revisions.
                state.status = "rejected"
                state.final = state.draft
                state.record("human", "orchestrator", "rejected")
                current = "DONE"

    return state


def run_topic(
    topic: str,
    *,
    audience: str = "general readers",
    tone: str = "friendly and informative",
    max_revisions: int | None = None,
    offline: bool = True,
    model: str | None = None,
    approver: Approver | None = None,
    on_event: EventHook | None = None,
) -> TeamState:
    """Convenience: build a fresh TeamState from a topic and run the team on it."""
    from . import DEFAULT_MAX_REVISIONS

    state = TeamState(
        topic=topic,
        audience=audience,
        tone=tone,
        max_revisions=DEFAULT_MAX_REVISIONS if max_revisions is None else max_revisions,
    )
    return run_team(
        state, offline=offline, model=model, approver=approver, on_event=on_event
    )
