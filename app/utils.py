from pathlib import Path


OUTPUT_DIR = Path("output")


class VideoNoteError(Exception):
    """Readable application error for expected failures."""


def ensure_output_dir() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def write_text_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collapse_whitespace(text: str) -> str:
    return " ".join(text.split())
