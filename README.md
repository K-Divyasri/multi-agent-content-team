# Multi-Agent Content Team

A **Researcher**, a **Writer**, and an **Editor** collaborate to write a blog post,
passing work between each other through a hand-rolled **orchestrator**, and a human has
the final say.

**Problem:** Asking one model to "research, write, and edit a great post" in a single
shot makes it hold three mindsets at once, and nothing checks its work. Split the job
across role-specialised agents and they hand drafts back and forth, catch each other's
gaps, and produce something better, the way a real content team does. The hard part
isn't the agents; it's the thing that routes work between them.

**Skills demonstrated:** multi-agent orchestration, role design, agent handoffs, an
explicit state machine (with a revision loop and a stop condition), human-in-the-loop
approval, provider-agnostic model calls via LiteLLM.

**Tech stack:** Python 3.10+, a hand-rolled orchestrator (no LangGraph/CrewAI needed to
learn the idea), LiteLLM (optional, for real models), Streamlit (optional, for the web
demo), pytest. Runs **offline with no API key** by default.

## Run it

```powershell
python -m venv .venv ; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt        # only needed for --real / the web app / tests
python -m content_team "how sleep affects learning"
```

You'll see the team collaborate live:

```
[researcher] gathered 5 bullets
[writer]     wrote the first draft
[editor]     REVISE -> Add an engaging hook in the opening to draw readers in.
[writer]     wrote the revision 1
[editor]     APPROVED
[human]      reviewing...
```

...followed by the handoff log (who handed what to whom) and the final post. Sit in the
approval seat yourself with `--interactive`, or run the agents on a real model with
`--real` (needs a free key in `.env`, see `.env.example`).

## Run the tests

```powershell
pytest
```

All 18 tests pass with **no API key and no network**: deterministic "fake agents" stand
in for a real LLM, so the whole suite (including the full research → write → edit → human
loop) runs on a bare laptop and in CI, for free.

## The web demo

```powershell
pip install streamlit
streamlit run web_app.py
```

Enter a topic, watch each agent work, then approve or reject the draft. Deploy it free,
see `hosting/HOSTING_GUIDE.md`.

## How it fits together

```
content_team/
  state.py         the shared TeamState every agent reads from and writes to
  agents.py        the three role agents (Researcher, Writer, Editor)
  llm.py           one model call, shared by all three (offline fake lives in agents.py)
  orchestrator.py  the STATE MACHINE that routes work between agents (the star)
  humanloop.py     the human approval gate (approve / revise / reject)
  cli.py           the terminal runner
web_app.py         the Streamlit UI (imports the package, adds no new logic)
```

## What I learned

- A multi-agent "system" is really a **state machine** over role-specialised agents; the
  agents are the easy part, the routing is the design.
- Handoffs need a shared **state object**, not a game of telephone: every agent updates
  one record.
- Any agent loop (the Editor bouncing a draft back to the Writer) needs a **stop
  condition**, or it can run forever. Here that's `max_revisions`.
- **Human-in-the-loop** is just a gate function; swapping auto-approve for a real person
  is a one-line change, which is exactly what makes this shippable rather than a demo.
