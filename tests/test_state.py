import json

from content_team.state import EditorReport, Handoff, TeamState


def test_state_defaults():
    s = TeamState(topic="x")
    assert s.audience and s.tone           # sensible defaults filled in
    assert s.research == [] and s.draft == ""
    assert s.status == "in_progress"
    assert s.max_revisions == 2


def test_record_appends_a_handoff():
    s = TeamState(topic="x")
    s.record("researcher", "writer", "5 bullets")
    assert s.log == [Handoff(frm="researcher", to="writer", note="5 bullets")]


def test_editor_report_is_approved():
    assert EditorReport(issues=[], verdict="approve").is_approved
    assert not EditorReport(issues=["x"], verdict="revise").is_approved


def test_state_serialises_to_json():
    s = TeamState(topic="x")
    s.record("a", "b")
    # to_dict() must be JSON-serialisable so a run can be saved as a transcript.
    text = json.dumps(s.to_dict())
    assert "topic" in text and "log" in text
