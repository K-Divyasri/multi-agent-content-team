from content_team.humanloop import auto_approve, make_scripted_approver
from content_team.orchestrator import run_team, run_topic
from content_team.state import TeamState


def test_full_run_ends_approved_with_a_final_post():
    state = run_topic("how sleep affects learning")
    assert state.status == "approved"
    assert state.final.startswith("# ")
    assert "## Conclusion" in state.final


def test_the_editor_loop_runs_exactly_once_and_converges():
    # The first draft is missing a hook, so the Editor bounces it back once; the
    # revision adds the hook, and the Editor approves. That's one revision, no more.
    state = run_topic("vector databases")
    assert state.revision_count == 1
    # The editor's FINAL verdict on the shipped draft is approve.
    assert state.editor_report.is_approved


def test_the_handoff_log_tells_the_collaboration_story():
    state = run_topic("remote work")
    pairs = [(h.frm, h.to) for h in state.log]
    # Researcher hands to writer, editor bounces back to writer, then editor -> human.
    assert ("researcher", "writer") in pairs
    assert ("editor", "writer") in pairs           # the revision handoff
    assert any(to == "human" for _, to in pairs)   # reached the human gate
    assert any(frm == "human" for frm, _ in pairs)  # the human acted


def test_revision_cap_stops_an_endless_loop():
    # An Editor that NEVER approves must not loop forever -- the cap sends it to the
    # human after max_revisions passes.
    def never_happy_edit(draft, **kwargs):
        from content_team.state import EditorReport
        return EditorReport(issues=["still not good enough"], verdict="revise")

    import content_team.orchestrator as orch
    original = orch.edit
    orch.edit = never_happy_edit
    try:
        state = TeamState(topic="anything", max_revisions=2)
        run_team(state, approver=auto_approve)
    finally:
        orch.edit = original
    assert state.revision_count == 2          # stopped exactly at the cap
    assert state.status in ("approved", "rejected")   # and finished


def test_human_can_send_it_back_then_approve():
    # The human gate bounces the draft once with a note, then approves the next pass.
    approver = make_scripted_approver([("revise", "make it punchier"), ("approve", "")])
    state = run_topic("productivity tips", approver=approver)
    assert state.status == "approved"
    # The human's revision is on top of the editor's, so we did more than one pass.
    assert state.revision_count >= 1
    assert any(h.frm == "human" and h.to == "writer" for h in state.log)


def test_human_can_reject():
    approver = make_scripted_approver([("reject", "")])
    state = run_topic("some topic", approver=approver)
    assert state.status == "rejected"
    assert state.final  # we still keep the draft that was rejected
