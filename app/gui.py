import threading
import tkinter as tk
import webbrowser
from tkinter import ttk

from app.downloader import download_subtitle, validate_youtube_url
from app.notes import generate_notes
from app.providers import list_providers
from app.theme import get_palette
from app.transcript import generate_transcript
from app.utils import VideoNoteError


# ── Palette (see app/theme.py — same tokens as the Chrome extension) ─────────
_PALETTE = get_palette()
BG      = _PALETTE["background"]
SURFACE = _PALETTE["card"]
BORDER  = _PALETTE["border"]
ACCENT  = _PALETTE["primary"]
TEXT    = _PALETTE["foreground"]
DIM     = _PALETTE["muted_foreground"]
LINK    = _PALETTE["secondary"]
ERR     = _PALETTE["destructive"]
OK      = "#2f9e6c"  # ponytail: no "success" token in the theme, kept as a plain constant
FONT    = "Helvetica"

def _shade(hex_color: str, factor: float) -> str:
    """Darken (factor < 0) or lighten (factor > 0) a hex color, for hover states."""
    r, g, b = (int(hex_color[i : i + 2], 16) for i in (1, 3, 5))

    def adjust(c: int) -> int:
        c = c + (255 - c) * factor if factor > 0 else c * (1 + factor)
        return max(0, min(255, round(c)))

    return "#{:02x}{:02x}{:02x}".format(adjust(r), adjust(g), adjust(b))


class App:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Video2Text")
        self.root.geometry("940x700")
        self.root.minsize(720, 540)
        self.root.configure(bg=BG)
        self._running = False
        self._video_title = ""
        self._video_url = ""
        self._providers = [p for p in list_providers() if p["available"]]
        self._provider_by_label = {p["label"]: p["id"] for p in self._providers}
        self._build()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self) -> None:
        self._build_header()
        self._build_input()
        self._build_status()
        self._build_tabs()

    def _build_header(self) -> None:
        bar = tk.Frame(self.root, bg=ACCENT, height=52)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)
        tk.Label(bar, text="Video2Text", bg=ACCENT, fg="#ffffff",
                 font=(FONT, 17, "bold")).pack(side=tk.LEFT, padx=20)
        tk.Label(bar, text="YouTube → Transcript & Notes",
                 bg=ACCENT, fg="#c5bef5",
                 font=(FONT, 12)).pack(side=tk.LEFT, padx=4)

    def _build_input(self) -> None:
        outer = tk.Frame(self.root, bg=BG, padx=20, pady=14)
        outer.pack(fill=tk.X)

        card = tk.Frame(outer, bg=SURFACE,
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill=tk.X)

        tk.Label(card, text="YouTube URL", bg=SURFACE, fg=DIM,
                 font=(FONT, 10)).pack(anchor=tk.W, padx=16, pady=(12, 3))

        row = tk.Frame(card, bg=SURFACE)
        row.pack(fill=tk.X, padx=16, pady=(0, 14))

        self.url_var = tk.StringVar()
        self.url_entry = tk.Entry(
            row, textvariable=self.url_var,
            font=(FONT, 13), bg="#f0f0f6", fg=TEXT, relief=tk.FLAT,
            highlightbackground=BORDER, highlightthickness=1,
            insertbackground=TEXT,
        )
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=9, padx=(0, 12))
        self.url_entry.bind("<Return>", lambda _e: self._start())

        self.btn = tk.Button(
            row, text="Generate", command=self._start,
            bg=ACCENT, fg="#ffffff",
            activebackground=_shade(ACCENT, -0.15), activeforeground="#ffffff",
            relief=tk.FLAT, cursor="hand2",
            font=(FONT, 12, "bold"), padx=22, pady=9,
        )
        self.btn.pack(side=tk.RIGHT)

        model_row = tk.Frame(card, bg=SURFACE)
        model_row.pack(fill=tk.X, padx=16, pady=(0, 14))

        tk.Label(model_row, text="Model", bg=SURFACE, fg=DIM,
                 font=(FONT, 10)).pack(side=tk.LEFT, padx=(0, 8))

        style = ttk.Style()
        style.configure("V2T.TCombobox", fieldbackground="#f0f0f6", background=SURFACE)

        self.model_var = tk.StringVar(
            value=self._providers[0]["label"] if self._providers else ""
        )
        self.model_combo = ttk.Combobox(
            model_row, textvariable=self.model_var,
            values=[p["label"] for p in self._providers],
            state="readonly", style="V2T.TCombobox",
            font=(FONT, 11), width=32,
        )
        self.model_combo.pack(side=tk.LEFT)

    def _build_status(self) -> None:
        bar = tk.Frame(self.root, bg=BG, padx=20, pady=2)
        bar.pack(fill=tk.X)

        self._status_var = tk.StringVar(value="Paste a YouTube URL above and click Generate.")
        self._status_lbl = tk.Label(
            bar, textvariable=self._status_var,
            bg=BG, fg=DIM, font=(FONT, 11),
        )
        self._status_lbl.pack(side=tk.LEFT)

        self._progress = ttk.Progressbar(bar, mode="indeterminate", length=100)

    def _build_tabs(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=BG, borderwidth=0, tabmargins=0)
        style.configure("TNotebook.Tab", background=BG, foreground=DIM,
                        font=(FONT, 11), padding=[18, 7])
        style.map("TNotebook.Tab",
                  background=[("selected", SURFACE)],
                  foreground=[("selected", ACCENT)])

        self._nb = ttk.Notebook(self.root)
        self._nb.pack(fill=tk.BOTH, expand=True, padx=20, pady=(8, 16))

        self._notes_text      = self._make_tab(self._nb, "  Notes  ")
        self._transcript_text = self._make_tab(self._nb, "  Transcript  ")

        for w in (self._notes_text, self._transcript_text):
            self._configure_tags(w)
            self._show_placeholder(w)

    def _make_tab(self, nb: ttk.Notebook, label: str) -> tk.Text:
        frame = tk.Frame(nb, bg=SURFACE)
        nb.add(frame, text=label)

        toolbar = tk.Frame(frame, bg=SURFACE)
        toolbar.pack(fill=tk.X, padx=14, pady=(10, 0))

        sb = tk.Scrollbar(frame, bg=BG, troughcolor=BG)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        widget = tk.Text(
            frame, bg=SURFACE, fg=TEXT,
            font=(FONT, 13), relief=tk.FLAT,
            wrap=tk.WORD, padx=30, pady=14,
            cursor="arrow", state=tk.DISABLED,
            selectbackground="#d0d0ee",
            yscrollcommand=sb.set,
        )
        widget.pack(fill=tk.BOTH, expand=True)
        sb.configure(command=widget.yview)

        copy_btn = tk.Button(
            toolbar, text="\U0001F4CB Copy", command=lambda: self._copy(widget),
            bg="#f0f0f6", fg=TEXT, relief=tk.FLAT, cursor="hand2",
            font=(FONT, 10), padx=10, pady=4,
            activebackground=BORDER,
        )
        copy_btn.pack(side=tk.LEFT)

        return widget

    def _configure_tags(self, w: tk.Text) -> None:
        w.tag_configure("h1",          font=(FONT, 22, "bold"), foreground=TEXT,
                        spacing1=4,    spacing3=6)
        w.tag_configure("link",        font=(FONT, 11), foreground=LINK,
                        underline=True, spacing3=14)
        w.tag_configure("h2",          font=(FONT, 15, "bold"), foreground=ACCENT,
                        spacing1=20,   spacing3=5)
        w.tag_configure("bullet",      font=(FONT, 13),         foreground=TEXT,
                        lmargin1=28,   lmargin2=46,
                        spacing1=4,    spacing3=4)
        w.tag_configure("body",        font=(FONT, 13),         foreground=TEXT,
                        spacing1=2,    spacing3=2)
        w.tag_configure("transcript",  font=(FONT, 13),         foreground=TEXT,
                        spacing1=6,    spacing2=5,   spacing3=16)
        w.tag_configure("placeholder", font=(FONT, 13, "italic"), foreground=DIM)

        w.tag_bind("link", "<Button-1>", lambda _e: webbrowser.open(self._video_url))
        w.tag_bind("link", "<Enter>", lambda _e: w.configure(cursor="hand2"))
        w.tag_bind("link", "<Leave>", lambda _e: w.configure(cursor="arrow"))

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _set_status(self, msg: str, color: str = DIM) -> None:
        self._status_var.set(msg)
        self._status_lbl.configure(fg=color)

    def _show_placeholder(self, w: tk.Text) -> None:
        w.configure(state=tk.NORMAL)
        w.delete("1.0", tk.END)
        w.insert("1.0", "Output will appear here after you generate notes.", "placeholder")
        w.configure(state=tk.DISABLED)

    def _insert_header(self, w: tk.Text) -> None:
        w.insert(tk.END, self._video_title + "\n", "h1")
        w.insert(tk.END, self._video_url + "\n", "link")

    def _copy(self, widget: tk.Text) -> None:
        content = widget.get("1.0", tk.END).rstrip("\n")
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.root.update()
        self._set_status("Copied to clipboard.", OK)

    # ── Rendering ─────────────────────────────────────────────────────────────

    def _render_notes(self, markdown: str) -> None:
        w = self._notes_text
        w.configure(state=tk.NORMAL)
        w.delete("1.0", tk.END)

        self._insert_header(w)

        skip_transcript = False
        for line in markdown.splitlines():
            if line.startswith("# "):
                continue  # title already shown in the header
            if line.startswith("## Transcript"):
                skip_transcript = True
                continue
            if skip_transcript:
                continue

            if line.startswith("## "):
                w.insert(tk.END, line[3:] + "\n", "h2")
            elif line.startswith("- "):
                w.insert(tk.END, "•  " + line[2:] + "\n", "bullet")
            elif line.strip():
                w.insert(tk.END, line + "\n", "body")
            else:
                w.insert(tk.END, "\n", "body")

        w.configure(state=tk.DISABLED)

    def _render_transcript(self, transcript: str) -> None:
        w = self._transcript_text
        w.configure(state=tk.NORMAL)
        w.delete("1.0", tk.END)

        self._insert_header(w)
        w.insert(tk.END, "\n", "body")

        for paragraph in transcript.split("\n\n"):
            w.insert(tk.END, paragraph + "\n", "transcript")

        w.configure(state=tk.DISABLED)

    # ── Generation ────────────────────────────────────────────────────────────

    def _start(self) -> None:
        if self._running:
            return
        url = self.url_var.get().strip()
        if not url:
            self._set_status("Please enter a YouTube URL.", ERR)
            return
        if not validate_youtube_url(url):
            self._set_status("Invalid URL — use a youtube.com/watch or youtu.be link.", ERR)
            return

        self._running = True
        self._video_url = url
        self.btn.configure(state=tk.DISABLED, text="Generating…")
        self._progress.pack(side=tk.RIGHT, padx=(10, 0))
        self._progress.start(10)

        provider = self._provider_by_label.get(self.model_var.get())
        threading.Thread(target=self._worker, args=(url, provider), daemon=True).start()

    def _worker(self, url: str, provider: str | None) -> None:
        try:
            self.root.after(0, self._set_status, "Reading video information…")
            info = download_subtitle(url)
            self._video_title = info["title"]

            self.root.after(0, self._set_status, f"Downloaded subtitles ({info['language']}).")
            transcript = generate_transcript(info["subtitle_path"])

            if not transcript:
                raise VideoNoteError("Subtitle file did not contain usable transcript text.")

            self.root.after(0, self._set_status, "Generating notes…")
            notes_md = generate_notes(info["title"], transcript, provider=provider)

            self.root.after(0, self._on_success, notes_md, transcript)
        except VideoNoteError as exc:
            self.root.after(0, self._on_error, str(exc))
        except Exception as exc:
            self.root.after(0, self._on_error, f"Unexpected error: {exc}")

    def _on_success(self, notes_md: str, transcript: str) -> None:
        self._running = False
        self._progress.stop()
        self._progress.pack_forget()
        self.btn.configure(state=tk.NORMAL, text="Generate")
        self._set_status("Done — files saved to output/", OK)
        self._render_notes(notes_md)
        self._render_transcript(transcript)
        self._nb.select(0)

    def _on_error(self, msg: str) -> None:
        self._running = False
        self._progress.stop()
        self._progress.pack_forget()
        self.btn.configure(state=tk.NORMAL, text="Generate")
        self._set_status(f"Error: {msg}", ERR)

    # ── Run ───────────────────────────────────────────────────────────────────

    def run(self) -> None:
        self.root.mainloop()
