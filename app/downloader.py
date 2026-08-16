from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from app.utils import VideoNoteError, ensure_output_dir


SUPPORTED_LANGUAGE_PREFIXES = ("en", "zh")


def validate_youtube_url(url: str) -> bool:
    parsed = urlparse(url.strip())
    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]

    if parsed.scheme not in {"http", "https"}:
        return False

    if host == "youtu.be":
        return bool(parsed.path.strip("/"))

    if host in {"youtube.com", "m.youtube.com"}:
        return parsed.path == "/watch" and "v=" in parsed.query

    return False


def get_video_info(url: str) -> dict:
    if not validate_youtube_url(url):
        raise VideoNoteError("Invalid YouTube URL. Provide a valid youtube.com/watch or youtu.be URL.")

    try:
        with YoutubeDL({"quiet": True, "skip_download": True, "noplaylist": True}) as ydl:
            return ydl.extract_info(url, download=False)
    except DownloadError as exc:
        raise VideoNoteError(f"Could not read video information: {exc}") from exc


def _language_rank(language: str) -> tuple[int, str]:
    lower = language.lower()
    if lower.startswith("en"):
        return (0, language)
    if lower.startswith("zh"):
        return (1, language)
    return (2, language)


def _find_supported_subtitle(info: dict) -> tuple[str, dict, bool]:
    subtitle_sets = [
        (info.get("subtitles") or {}, False),
        (info.get("automatic_captions") or {}, True),
    ]

    for subtitles, is_automatic in subtitle_sets:
        supported_languages = sorted(
            (
                language
                for language in subtitles
                if language.lower().startswith(SUPPORTED_LANGUAGE_PREFIXES)
            ),
            key=_language_rank,
        )

        for language in supported_languages:
            formats = subtitles.get(language) or []
            vtt_format = next((item for item in formats if item.get("ext") == "vtt"), None)
            if vtt_format and vtt_format.get("url"):
                return language, vtt_format, is_automatic

    raise VideoNoteError("No English or Chinese subtitles were found for this video.")


def download_subtitle(url: str, output_path: Path | None = None) -> dict:
    info = get_video_info(url)
    language, subtitle, is_automatic = _find_supported_subtitle(info)

    output_dir = ensure_output_dir()
    output_path = output_path or output_dir / "raw_subtitle.vtt"

    request = Request(subtitle["url"], headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urlopen(request, timeout=30) as response:
            subtitle_text = response.read().decode("utf-8")
    except (HTTPError, URLError, TimeoutError) as exc:
        raise VideoNoteError(f"Could not download subtitles: {exc}") from exc

    output_path.write_text(subtitle_text, encoding="utf-8")

    return {
        "title": info.get("title") or "Untitled Video",
        "language": language,
        "subtitle_path": output_path,
        "is_automatic": is_automatic,
    }
