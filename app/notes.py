from pathlib import Path
import re

from app.providers import HEURISTIC_ID, default_provider, generate as generate_from_provider
from app.utils import collapse_whitespace, write_text_file


SENTENCE_RE = re.compile(r"(?<=[.!?。！？])\s+")
ACTION_WORDS = (
    "should",
    "need to",
    "must",
    "try",
    "practice",
    "remember",
    "use",
    "avoid",
    "make sure",
)
ACTION_PATTERNS = [
    re.compile(rf"(?<!\w){re.escape(word)}(?!\w)", re.IGNORECASE)
    for word in ACTION_WORDS
]


def _sentences(transcript: str) -> list[str]:
    normalized = collapse_whitespace(transcript)
    return [sentence.strip() for sentence in SENTENCE_RE.split(normalized) if sentence.strip()]


def generate_summary(transcript: str) -> str:
    sentences = _sentences(transcript)
    if not sentences:
        return "No transcript content available."
    return " ".join(sentences[:3])


def generate_key_points(transcript: str) -> list[str]:
    sentences = _sentences(transcript)
    points = sentences[:3]

    while len(points) < 3:
        points.append("Review the transcript for additional details.")

    return points[:3]


def generate_action_items(transcript: str) -> list[str]:
    sentences = _sentences(transcript)
    actions = [
        sentence
        for sentence in sentences
        if any(pattern.search(sentence) for pattern in ACTION_PATTERNS)
    ]

    if not actions:
        return ["No explicit action items found."]

    return actions[:5]


def generate_notes(
    title: str,
    transcript: str,
    output_path: Path | None = None,
    provider: str | None = None,
) -> str:
    provider_id = provider or default_provider()

    llm_notes = None
    if provider_id != HEURISTIC_ID:
        llm_notes = generate_from_provider(provider_id, title, transcript)

    if llm_notes is not None:
        summary = llm_notes["summary"]
        key_points = llm_notes["key_points"]
        action_items = llm_notes["action_items"]
    else:
        summary = generate_summary(transcript)
        key_points = generate_key_points(transcript)
        action_items = generate_action_items(transcript)

    markdown = "\n".join(
        [
            f"# {title}",
            "",
            "## Summary",
            "",
            summary,
            "",
            "## Key Points",
            "",
            *[f"- {point}" for point in key_points],
            "",
            "## Action Items",
            "",
            *[f"- {item}" for item in action_items],
            "",
            "## Transcript",
            "",
            transcript.strip(),
            "",
        ]
    )

    output_path = output_path or Path("output/notes.md")
    write_text_file(output_path, markdown)
    return markdown
