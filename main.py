import sys

from app.downloader import download_subtitle, validate_youtube_url
from app.notes import generate_notes
from app.transcript import generate_transcript
from app.utils import VideoNoteError


def run(url: str) -> None:
    if not validate_youtube_url(url):
        raise VideoNoteError("Invalid YouTube URL. Provide a valid youtube.com/watch or youtu.be URL.")

    print("Reading video information...")
    subtitle_info = download_subtitle(url)
    print(f"Downloaded subtitles ({subtitle_info['language']}).")

    print("Generating transcript...")
    transcript = generate_transcript(subtitle_info["subtitle_path"])
    if not transcript:
        raise VideoNoteError("Subtitle file did not contain usable transcript text.")

    print("Generating notes with Claude...")
    generate_notes(subtitle_info["title"], transcript)

    print("Done.")
    print("Created output/transcript.txt")
    print("Created output/notes.md")


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python main.py <youtube_url>", file=sys.stderr)
        return 1

    try:
        run(sys.argv[1])
    except VideoNoteError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Error: interrupted.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
