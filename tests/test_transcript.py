from pathlib import Path

from app.transcript import generate_transcript, parse_vtt, to_paragraphs


SAMPLE_VTT = """WEBVTT

00:00:00.000 --> 00:00:02.000
Hello <c>world</c>.

00:00:02.000 --> 00:00:04.000
Hello <c>world</c>.

00:00:04.000 --> 00:00:06.000
This is a transcript line.
"""

MULTI_SENTENCE_VTT = """WEBVTT

00:00:00.000 --> 00:00:02.000
One sentence.

00:00:02.000 --> 00:00:04.000
Two sentence.

00:00:04.000 --> 00:00:06.000
Three sentence.

00:00:06.000 --> 00:00:08.000
Four sentence.
"""


def test_parse_vtt_removes_metadata_timestamps_and_duplicate_lines():
    assert parse_vtt(SAMPLE_VTT) == "Hello world.\nThis is a transcript line."


def test_to_paragraphs_puts_each_sentence_on_its_own_line_without_needing_a_model():
    text = "One sentence. Two sentence. Three sentence."
    assert to_paragraphs(text) == "One sentence.\n\nTwo sentence.\n\nThree sentence."


def test_generate_transcript_writes_one_sentence_per_line(tmp_path):
    subtitle_path = tmp_path / "sample.vtt"
    output_path = tmp_path / "transcript.txt"
    subtitle_path.write_text(MULTI_SENTENCE_VTT, encoding="utf-8")

    transcript = generate_transcript(Path(subtitle_path), output_path)

    assert transcript == (
        "One sentence.\n\nTwo sentence.\n\nThree sentence.\n\nFour sentence."
    )
    assert output_path.read_text(encoding="utf-8") == transcript + "\n"
