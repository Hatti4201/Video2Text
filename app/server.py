import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from app.downloader import download_subtitle, validate_youtube_url
from app.notes import generate_notes
from app.providers import list_providers
from app.transcript import generate_transcript
from app.utils import VideoNoteError

PORT = 8756
HOST = os.environ.get("HOST", "127.0.0.1")
# ponytail: shared-secret header, no accounts/OAuth — this is a single-user
# personal server, the only threat model is "random internet stranger finds
# the URL and burns my LLM credits". Set API_TOKEN to require it; unset (the
# local-dev default) skips the check entirely.
API_TOKEN = os.environ.get("API_TOKEN")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):  # noqa: A002 - stdlib signature
        pass

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Api-Token")
        self.end_headers()

    def _authorized(self) -> bool:
        if not API_TOKEN:
            return True
        return hmac.compare_digest(self.headers.get("X-Api-Token", ""), API_TOKEN)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send_json(200, {"status": "ok"})
        elif self.path == "/providers":
            if not self._authorized():
                self._send_json(401, {"error": "Unauthorized"})
                return
            self._send_json(200, {"providers": list_providers()})
        else:
            self._send_json(404, {"error": "Not found"})

    def do_POST(self) -> None:
        if self.path != "/generate":
            self._send_json(404, {"error": "Not found"})
            return
        if not self._authorized():
            self._send_json(401, {"error": "Unauthorized"})
            return

        length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid JSON body."})
            return

        url = str(data.get("url") or "").strip()
        provider = data.get("provider") or None
        if not validate_youtube_url(url):
            self._send_json(400, {"error": "Invalid YouTube URL."})
            return

        try:
            info = download_subtitle(url)
            transcript = generate_transcript(info["subtitle_path"])
            if not transcript:
                raise VideoNoteError("Subtitle file did not contain usable transcript text.")
            notes_md = generate_notes(info["title"], transcript, provider=provider)
        except VideoNoteError as exc:
            self._send_json(422, {"error": str(exc)})
            return
        except Exception as exc:  # keep the extension informed instead of hanging
            self._send_json(500, {"error": f"Unexpected error: {exc}"})
            return

        self._send_json(
            200,
            {
                "title": info["title"],
                "language": info["language"],
                "transcript": transcript,
                "notes_markdown": notes_md,
            },
        )


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Video2Text server running at http://{HOST}:{PORT}")
    print("Keep this window open while using the Chrome extension. Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
