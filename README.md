# Video2Text

*[中文说明](README.zh-CN.md)*

Turn any YouTube video into structured notes.

Paste a YouTube URL and get two files:

- `output/transcript.txt` — the full spoken text of the video
- `output/notes.md` — a Markdown document with a summary, key points, action items, and the full transcript

The summary, key points, and action items are written by an AI model — Claude by default, with GPT, Gemini, DeepSeek, Qwen, and others also supported.

Three ways to use it: a command-line script, a desktop GUI, and a browser-only
Chrome extension that reads existing captions on the YouTube watch page.

---

## What it does

```
YouTube URL
    ↓
Download subtitles (English or Chinese)
    ↓
Clean up the raw subtitle file into a readable transcript
    ↓
Send the transcript to an AI provider to write a summary, key points, and action items
    ↓
Save transcript.txt and notes.md to the output/ folder
```

If no AI provider is configured, the tool falls back to a simple pattern-matching summary so it still produces output, but the notes will be lower quality.

---

## Getting started

**📖 See the [Usage guide](docs/usage.md)** for installation, API key setup
(including all supported providers), and how to run the CLI, the desktop
GUI, and the Chrome extension.

---

## Project structure

```
Video2Text/
├── app/
│   ├── downloader.py     # Downloads subtitles from YouTube
│   ├── transcript.py     # Parses VTT subtitle files into plain text
│   ├── notes.py          # Generates structured notes via an AI provider (with a heuristic fallback)
│   ├── providers.py      # AI provider registry (Claude, GPT, Gemini, Qwen, DeepSeek, ...)
│   ├── theme.py          # Shared color theme (used by the desktop GUI)
│   ├── server.py         # Optional local HTTP interface
│   ├── gui.py            # Desktop GUI (Tkinter)
│   └── utils.py          # Shared utilities
├── extension/            # Browser-only Chrome extension for existing captions
│   └── theme.css          # Shared color theme (same tokens as app/theme.py)
├── output/               # Generated files are saved here
├── tests/                # Automated tests
├── docs/                 # Project documentation, including the usage guide
├── main.py               # CLI entry point
├── ui.py                 # Desktop GUI entry point
└── requirements.txt
```

---

## Future roadmap

```
Phase 1 - MVP (current)
Phase 2 - Cloud LLM notes (current) / Local LLM option
Phase 3 - Whisper (audio transcription without subtitles)
Phase 4 - Notion integration
Phase 5 - Telegram integration
Phase 6 - Docker
Phase 7 - Windows deployment
Phase 8 - Secure remote access
Phase 9 - Knowledge system
Phase 10 - Personal assistant ecosystem
```
