"""content_team -- three specialised agents that collaborate to write a blog post.

The idea this project teaches: instead of asking one model to "write a great blog
post" in a single shot, you split the job across a small TEAM of role-specialised
agents that hand work to each other, exactly like a real content team:

    Researcher -> gathers the facts and angles
    Writer     -> turns that research into a draft
    Editor     -> reviews the draft and either approves it or sends it back

And a human sits at the end with an approval gate: approve, or bounce it back with
notes. That back-and-forth -- the Editor returning a draft to the Writer, the human
requesting another pass -- is the whole point. It's a loop, not a straight line.

What actually makes this work is NOT the agents; it's the thing that moves work
between them. That's the **orchestrator**: a small explicit state machine that knows
who goes next based on what just happened. Being able to draw that state machine, and
say why a real system needs one, is the senior-level signal this project is built to
give you.

The pieces, each readable on its own:

    state.py         the shared TeamState that flows through the whole pipeline
    agents.py        the three role agents (Researcher, Writer, Editor)
    llm.py           one model call, with an OFFLINE fake so it runs free
    orchestrator.py  the state machine that routes work between agents (the star)
    humanloop.py     the human approval gate (approve / revise / reject)
    cli.py           run the team on a topic from the terminal

Everything runs OFFLINE by default with deterministic "fake agents", so the notebooks,
the tests, and the CLI all work on a fresh laptop with no API key. Add a free key and
pass offline=False to run the same pipeline on a real model through LiteLLM.
"""

from __future__ import annotations

# How many times the Writer is allowed to redo the draft before we stop looping and
# hand it to the human no matter what. Without a cap, an over-picky Editor (or a buggy
# one) could bounce a draft forever -- every real agent loop needs a stop condition.
DEFAULT_MAX_REVISIONS = 2

__all__ = ["DEFAULT_MAX_REVISIONS"]
