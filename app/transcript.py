from pathlib import Path
import re

from app.utils import collapse_whitespace, write_text_file


TIMESTAMP_RE = re.compile(r"^\d{2}:\d{2}:\d{2}\.\d{3}\s+-->\s+\d{2}:\d{2}:\d{2}\.\d{3}")
HTML_TAG_RE = re.compile(r"<[^>]+>")
SENTENCE_RE = re.compile(r"(?<=[.!?。！？])\s+")
SENTENCES_PER_PARAGRAPH = 1


def parse_vtt(vtt_text: str) -> str:
    lines: list[str] = []
    previous = ""

    for raw_line in vtt_text.splitlines():
        line = raw_line.strip()

        if not line:
            continue
        if line == "WEBVTT" or line.startswith(("Kind:", "Language:", "NOTE")):
            continue
        if TIMESTAMP_RE.match(line):
            continue
        if line.isdigit():
            continue

        cleaned = HTML_TAG_RE.sub("", line).replace("&amp;", "&")
        cleaned = collapse_whitespace(cleaned)
        if cleaned and cleaned != previous:
            lines.append(cleaned)
            previous = cleaned

    return "\n".join(lines).strip()


def to_paragraphs(text: str) -> str:
    """Put each sentence on its own line. Not semantic — just sentence
    boundaries — so this works the same with or without an AI model."""
    sentences = [s.strip() for s in SENTENCE_RE.split(collapse_whitespace(text)) if s.strip()]
    if not sentences:
        return text.strip()

    paragraphs = [
        " ".join(sentences[i : i + SENTENCES_PER_PARAGRAPH])
        for i in range(0, len(sentences), SENTENCES_PER_PARAGRAPH)
    ]
    return "\n\n".join(paragraphs)


def generate_transcript(subtitle_path: Path, output_path: Path | None = None) -> str:
    transcript = to_paragraphs(parse_vtt(subtitle_path.read_text(encoding="utf-8")))
    output_path = output_path or Path("output/transcript.txt")
    write_text_file(output_path, transcript + "\n")
    return transcript
