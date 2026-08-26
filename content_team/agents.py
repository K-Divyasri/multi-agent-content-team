"""The three role agents: Researcher, Writer, Editor.

An "agent" here is not some autonomous robot -- it's a **role**: a system prompt plus a
single model call, specialised to do one job well. That specialisation is the whole
argument for multi-agent systems. One prompt that says "research, then write, then
edit" asks a model to hold three mindsets at once. Three focused prompts each do one
thing, and they check each other's work.

Each agent has two implementations behind one function:

  offline  a deterministic 'fake' that behaves like the role (the Researcher really
           does produce bullets; the Editor really does return a verdict), so the whole
           pipeline runs with no key. It is NOT a language model -- it's rules -- but it
           is written so the TEAM behaves correctly: the first draft is missing a hook,
           the Editor catches exactly that, the Writer fixes it, the Editor approves.
           That little arc is the multi-agent loop, made testable.

  real     a LiteLLM call with the role's system prompt. Same interface, real output.
"""

from __future__ import annotations

import re

from .llm import call_model
from .state import EditorReport, TeamState

# --------------------------------------------------------------------------- #
#  The role system prompts (used by the REAL agents, and shown in the UI/docs) #
# --------------------------------------------------------------------------- #
RESEARCHER_SYSTEM = (
    "You are a meticulous researcher. Given a topic and an audience, produce 4-6 "
    "concise, factual bullet points a writer could build an article from. Put one "
    "idea per bullet, and start each bullet with a short label followed by a colon "
    "(e.g. 'Why it matters: ...'). Output only the bullets, one per line."
)

WRITER_SYSTEM = (
    "You are a skilled blog writer. Turn the research bullets into a clear, engaging "
    "post: an H1 title (a single '# ' line), an opening hook, one short '## ' section "
    "per research point, and a '## Conclusion'. Honour the requested tone and "
    "audience. If you are given editor feedback, revise the draft to address every "
    "point in it. Output the post in Markdown."
)

EDITOR_SYSTEM = (
    "You are a sharp editor. Review the draft for: a clear H1 title, an engaging hook "
    "in the opening, a section for each point, and a conclusion. List concrete issues "
    "as '- ' bullet lines. Then end with a line exactly of the form 'VERDICT: approve' "
    "or 'VERDICT: revise'. Approve only if the draft is genuinely publication-ready."
)


# --------------------------------------------------------------------------- #
#  Small shared helpers                                                       #
# --------------------------------------------------------------------------- #
def _title(topic: str) -> str:
    return topic.strip().rstrip(".").title()


def _label_and_body(bullet: str) -> tuple[str, str]:
    """Split a 'Label: sentence' bullet into (label, sentence). Degrades gracefully."""
    if ":" in bullet:
        label, body = bullet.split(":", 1)
        return label.strip(), body.strip()
    return bullet.strip(), bullet.strip()


# --------------------------------------------------------------------------- #
#  Researcher                                                                 #
# --------------------------------------------------------------------------- #
def fake_research(topic: str, audience: str) -> list[str]:
    """Deterministic research bullets. Real research is smarter; this is enough to run."""
    return [
        f"Definition: what {topic} actually is, in one plain sentence.",
        f"Why it matters: the concrete payoff of {topic} for {audience}.",
        f"Common mistake: the misconception about {topic} that trips people up.",
        f"Example: an everyday case of {topic} in action.",
        f"Getting started: one practical first step with {topic}.",
    ]


def _parse_bullets(text: str) -> list[str]:
    """Pull bullet lines out of a real model's research output."""
    bullets = []
    for line in text.splitlines():
        line = line.strip()
        line = re.sub(r"^[-*\d.)\s]+", "", line)  # strip bullet/number markers
        if line:
            bullets.append(line)
    return bullets or [text.strip()]


def research(state: TeamState, *, offline: bool = True, model: str | None = None) -> list[str]:
    """The Researcher: turn the brief into bullet points."""
    if offline:
        return fake_research(state.topic, state.audience)
    user = f"Topic: {state.topic}\nAudience: {state.audience}\nProduce the research bullets."
    return _parse_bullets(call_model(RESEARCHER_SYSTEM, user, model=model, temperature=0.4))


# --------------------------------------------------------------------------- #
#  Writer                                                                     #
# --------------------------------------------------------------------------- #
# A hook is an opening line that pulls the reader in. The first draft deliberately
# omits one; the Editor asks for it; this marker is how both sides agree it's there.
_HOOK_MARK = "Ever wondered"


def fake_write(state: TeamState) -> str:
    """Deterministically assemble a blog post from the research (and any feedback).

    The one behaviour that matters for the demo: this draft has NO hook UNTIL the
    feedback asks for one. That's what lets the Editor -> Writer -> Editor loop
    actually converge instead of looping forever or approving junk.
    """
    title = _title(state.topic)
    add_hook = "hook" in state.feedback.lower()

    lines = [f"# {title}", ""]
    if add_hook:
        lines.append(
            f"{_HOOK_MARK} about {state.topic}? You're not alone -- and it's more "
            "approachable than it first looks. Let's break it down."
        )
        lines.append("")
    lines.append(
        f"{title} matters more than you might think for {state.audience}. "
        f"Here's a {state.tone} tour of what actually counts."
    )
    for i, bullet in enumerate(state.research, 1):
        label, body = _label_and_body(bullet)
        lines.append("")
        lines.append(f"## {label}")
        lines.append(body[:1].upper() + body[1:] if body else f"Point {i}.")
    lines.append("")
    lines.append("## Conclusion")
    lines.append(
        f"That's the short tour of {state.topic}. Start small, stay curious, "
        "and it'll click sooner than you expect."
    )
    return "\n".join(lines)


def write(state: TeamState, *, offline: bool = True, model: str | None = None) -> str:
    """The Writer: draft (or revise) the post from research + any editor/human feedback."""
    if offline:
        return fake_write(state)
    bullets = "\n".join(f"- {b}" for b in state.research)
    user = (
        f"Topic: {state.topic}\nAudience: {state.audience}\nTone: {state.tone}\n\n"
        f"Research bullets:\n{bullets}\n"
    )
    if state.feedback:
        user += f"\nEditor/human feedback to address in this revision:\n{state.feedback}\n"
        user += "\nRewrite the full post addressing every point above."
    else:
        user += "\nWrite the full post."
    return call_model(WRITER_SYSTEM, user, model=model, temperature=0.7)


# --------------------------------------------------------------------------- #
#  Editor                                                                     #
# --------------------------------------------------------------------------- #
def fake_edit(draft: str) -> EditorReport:
    """Deterministically review a draft against a small, concrete rubric."""
    issues: list[str] = []
    if not draft.lstrip().startswith("# "):
        issues.append("Add a clear H1 title at the very top.")
    if _HOOK_MARK not in draft:
        issues.append("Add an engaging hook in the opening to draw readers in.")
    if "## conclusion" not in draft.lower() and "in conclusion" not in draft.lower():
        issues.append("Add a conclusion that summarises the takeaways.")
    verdict = "approve" if not issues else "revise"
    return EditorReport(issues=issues, verdict=verdict)


def _parse_editor(text: str) -> EditorReport:
    """Read a real editor's reply: '- issue' lines plus a 'VERDICT: ...' line."""
    issues = []
    verdict = "revise"
    for line in text.splitlines():
        s = line.strip()
        m = re.match(r"verdict\s*:\s*(approve|revise)", s, re.IGNORECASE)
        if m:
            verdict = m.group(1).lower()
        elif s.startswith(("-", "*")):
            issue = s.lstrip("-* ").strip()
            if issue:
                issues.append(issue)
    if verdict == "approve":
        issues = []  # an approval means no blocking issues remain
    return EditorReport(issues=issues, verdict=verdict)


def edit(draft: str, *, offline: bool = True, model: str | None = None) -> EditorReport:
    """The Editor: review a draft and return an approve/revise verdict with issues."""
    if offline:
        return fake_edit(draft)
    return _parse_editor(call_model(EDITOR_SYSTEM, f"Draft to review:\n\n{draft}", model=model, temperature=0.2))
