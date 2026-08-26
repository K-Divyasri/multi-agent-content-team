"""A Streamlit UI for the content team -- what you deploy for a public URL.

This file is deliberately thin: all the real work (the agents, the orchestrator, the
human gate) lives in the `content_team` package and is reused here. The web app only
draws the page -- a topic box, a live view of each agent working, the human approve/
revise/reject buttons, and the final post.

Run it locally with:

    streamlit run web_app.py

By default it runs the OFFLINE fake agents, so the public demo costs nothing and needs
no key. Flip on "Use a real model" in the sidebar and provide a key to run the same
pipeline on a real model through LiteLLM.
"""

from __future__ import annotations

import os

import streamlit as st

from content_team.agents import edit, research, write
from content_team.llm import DEFAULT_MODEL
from content_team.state import TeamState

st.set_page_config(page_title="Content Team", page_icon=None, layout="centered")
st.title("Multi-Agent Content Team")
st.caption(
    "A Researcher, a Writer, and an Editor collaborate to write a blog post -- and you "
    "get the final say. Offline by default; no API key needed."
)


def get_api_key() -> str | None:
    for name in ("GEMINI_API_KEY", "GROQ_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
        try:
            if name in st.secrets:
                return st.secrets[name]
        except Exception:
            pass
        if os.environ.get(name):
            return os.environ[name]
    return None


with st.sidebar:
    st.header("The brief")
    topic = st.text_input("Topic", value="how sleep affects learning")
    audience = st.text_input("Audience", value="general readers")
    tone = st.text_input("Tone", value="friendly and informative")
    max_revisions = st.slider("Max editor revisions", 0, 4, 2)

    use_real = st.toggle("Use a real model (needs a key)", value=False)
    model = DEFAULT_MODEL
    if use_real:
        model = st.text_input("Model (LiteLLM string)", value=DEFAULT_MODEL)
        key = get_api_key()
        if key:
            for name in ("GEMINI_API_KEY", "GROQ_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
                try:
                    if name in st.secrets:
                        os.environ[name] = st.secrets[name]
                except Exception:
                    pass
        else:
            st.info("No API key found -- falling back to the offline agents.")
            use_real = False

    start = st.button("Run the team", type="primary")

offline = not use_real

# We run the pipeline "by hand" here (research -> write -> edit loop) rather than calling
# run_team, because the web app's human gate is a pair of buttons, not a function that
# blocks. The stages are the same ones the orchestrator drives; we just pause at the gate.
if start:
    state = TeamState(topic=topic, audience=audience, tone=tone, max_revisions=max_revisions)

    with st.status("The team is working...", expanded=True) as status:
        st.write("**Researcher** is gathering facts...")
        state.research = research(state, offline=offline, model=model)
        st.write(f"Got {len(state.research)} research bullets.")

        while True:
            tag = f"revision {state.revision_count}" if state.revision_count else "first draft"
            st.write(f"**Writer** is drafting the {tag}...")
            state.draft = write(state, offline=offline, model=model)

            st.write("**Editor** is reviewing...")
            report = edit(state.draft, offline=offline, model=model)
            state.editor_report = report

            if report.is_approved or state.revision_count >= state.max_revisions:
                if report.is_approved:
                    st.write("Editor **approved** the draft.")
                else:
                    st.write("Editor still has notes, but we've hit the revision cap.")
                break

            st.write(f"Editor asked for a **revision**: {'; '.join(report.issues)}")
            state.revision_count += 1
            state.feedback = "; ".join(report.issues)

        status.update(label="Ready for your review", state="complete")

    # Stash the finished-by-the-team state so the human-gate buttons can act on it.
    st.session_state.state = state

# The human gate: show the draft and let the person decide.
if "state" in st.session_state:
    state = st.session_state.state

    with st.expander("Research bullets", expanded=False):
        for b in state.research:
            st.write("- " + b)

    with st.expander("How the team collaborated (handoffs)", expanded=False):
        for h in state.log:
            st.write(f"`{h.frm}` -> `{h.to}` {('- ' + h.note) if h.note else ''}")

    if state.status == "in_progress":
        st.subheader("Human review")
        st.caption("The team thinks this is ready. You decide.")
        st.markdown(state.draft)
        col1, col2 = st.columns(2)
        if col1.button("Approve and ship"):
            state.status = "approved"
            state.final = state.draft
            st.rerun()
        if col2.button("Reject"):
            state.status = "rejected"
            state.final = state.draft
            st.rerun()
    else:
        badge = "APPROVED" if state.status == "approved" else "REJECTED"
        st.subheader(f"Final post ({badge})")
        st.markdown(state.final or state.draft)
        st.download_button(
            "Download the post (.md)",
            data=state.final or state.draft,
            file_name="post.md",
            mime="text/markdown",
        )
