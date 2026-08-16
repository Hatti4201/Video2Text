from app.notes import generate_action_items, generate_key_points, generate_notes, generate_summary


TRANSCRIPT = (
    "This video explains how to take useful notes. "
    "You should capture the main idea. "
    "Avoid copying every sentence. "
    "Practice reviewing notes after watching."
)


def test_generate_summary_uses_initial_sentences():
    summary = generate_summary(TRANSCRIPT)
    assert "This video explains" in summary
    assert "You should capture" in summary


def test_generate_key_points_returns_at_least_three_points():
    assert len(generate_key_points("One sentence.")) == 3


def test_generate_action_items_extracts_actionable_sentences():
    actions = generate_action_items(TRANSCRIPT)
    assert actions == [
        "You should capture the main idea.",
        "Avoid copying every sentence.",
        "Practice reviewing notes after watching.",
    ]


def test_generate_notes_contains_required_sections(tmp_path):
    output_path = tmp_path / "notes.md"
    notes = generate_notes("Sample Title", TRANSCRIPT, output_path)

    assert "# Sample Title" in notes
    assert "## Summary" in notes
    assert "## Key Points" in notes
    assert "## Action Items" in notes
    assert "## Transcript" in notes
    assert output_path.read_text(encoding="utf-8") == notes
