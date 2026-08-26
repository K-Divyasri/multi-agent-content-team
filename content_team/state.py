"""The shared state that flows through the team.

Multi-agent systems live or die on ONE design question: how do the agents share
work? The clean answer is a single **state object** that every agent reads from and
writes to. The Researcher fills in `research`; the Writer reads `research` and fills
in `draft`; the Editor reads `draft` and fills in `editor_report`. Nobody passes long
messages around -- they all just update one shared record.

This module is that record. It's plain data (a dataclass), so you can print it, save
it, or diff it at any point in the run and see exactly where the work is.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class Handoff:
    """One recorded 'X handed the work to Y' event -- the team's paper trail."""

    frm: str  # who was working ("researcher", "editor", "human", "orchestrator")
    to: str  # who gets it next
    note: str = ""  # a short why ("draft", "revise: add a hook", "approved")


@dataclass
class EditorReport:
    """The Editor's verdict on a draft."""

    issues: list[str]  # concrete problems found (empty if none)
    verdict: str  # "approve" or "revise"

    @property
    def is_approved(self) -> bool:
        return self.verdict == "approve"


@dataclass
class TeamState:
    """Everything the team is working on, in one place. Agents mutate this in turn."""

    # -- the brief (set by whoever kicks off the run) ------------------------ #
    topic: str
    audience: str = "general readers"
    tone: str = "friendly and informative"

    # -- filled in as the pipeline runs -------------------------------------- #
    research: list[str] = field(default_factory=list)  # Researcher's bullets
    draft: str = ""  # Writer's current draft
    editor_report: EditorReport | None = None  # Editor's latest verdict
    feedback: str = ""  # notes handed to the Writer for the next revision

    # -- control / bookkeeping ---------------------------------------------- #
    revision_count: int = 0  # how many times the Writer has redone the draft
    max_revisions: int = 2  # the cap, so the loop always terminates
    status: str = "in_progress"  # "in_progress" | "approved" | "rejected"
    final: str = ""  # the post we ship (set when the run ends)
    log: list[Handoff] = field(default_factory=list)  # every handoff, in order

    def record(self, frm: str, to: str, note: str = "") -> None:
        """Add a handoff to the paper trail. The orchestrator calls this on every step."""
        self.log.append(Handoff(frm=frm, to=to, note=note))

    def to_dict(self) -> dict:
        """A plain dict you can json.dump -- handy for saving a run transcript."""
        return asdict(self)
