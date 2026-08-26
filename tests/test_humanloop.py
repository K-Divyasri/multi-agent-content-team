from content_team.humanloop import (
    auto_approve,
    make_cli_approver,
    make_scripted_approver,
)
from content_team.state import TeamState


def test_auto_approve_always_approves():
    assert auto_approve(TeamState(topic="x")) == ("approve", "")


def test_scripted_approver_returns_decisions_in_order():
    approver = make_scripted_approver([("revise", "punchier"), ("approve", "")])
    s = TeamState(topic="x")
    assert approver(s) == ("revise", "punchier")
    assert approver(s) == ("approve", "")
    # Once the script runs out, it defaults to approve (so runs never hang).
    assert approver(s) == ("approve", "")


def test_cli_approver_reads_a_choice(monkeypatch):
    # Feed canned keystrokes: 'r' then the revision note.
    answers = iter(["r", "tighten the intro"])
    approver = make_cli_approver(input_fn=lambda prompt: next(answers))
    s = TeamState(topic="x")
    s.draft = "# Draft"
    assert approver(s) == ("revise", "tighten the intro")


def test_cli_approver_approve_and_reject(monkeypatch):
    approve = make_cli_approver(input_fn=lambda prompt: "a")
    reject = make_cli_approver(input_fn=lambda prompt: "x")
    s = TeamState(topic="x")
    s.draft = "# Draft"
    assert approve(s) == ("approve", "")
    assert reject(s) == ("reject", "")
