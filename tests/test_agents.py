from content_team.agents import (
    fake_edit,
    fake_research,
    fake_write,
    _HOOK_MARK,
)
from content_team.state import TeamState


def test_researcher_produces_several_labelled_bullets():
    bullets = fake_research("vector databases", "developers")
    assert len(bullets) >= 4
    assert all(":" in b for b in bullets)          # "Label: sentence" shape
    assert any("vector databases" in b for b in bullets)


def test_first_draft_has_title_and_conclusion_but_no_hook():
    state = TeamState(topic="sleep and learning")
    state.research = fake_research(state.topic, state.audience)
    draft = fake_write(state)
    assert draft.lstrip().startswith("# ")          # has an H1 title
    assert "## Conclusion" in draft                  # has a conclusion
    assert _HOOK_MARK not in draft                   # but NO hook on the first pass


def test_editor_flags_the_missing_hook_then_approves_once_added():
    state = TeamState(topic="sleep and learning")
    state.research = fake_research(state.topic, state.audience)

    first = fake_write(state)
    report1 = fake_edit(first)
    assert report1.verdict == "revise"
    assert any("hook" in issue.lower() for issue in report1.issues)

    # The Writer revises with the editor's feedback...
    state.feedback = "; ".join(report1.issues)
    revised = fake_write(state)
    assert _HOOK_MARK in revised                     # the hook is now present

    # ...and the Editor approves the revised draft.
    report2 = fake_edit(revised)
    assert report2.verdict == "approve"
    assert report2.issues == []


def test_editor_report_is_approved_helper():
    ok = fake_edit("# T\n\nEver wondered? yes.\n\n## Conclusion\ndone")
    assert ok.is_approved is True
