# Usage guide

*[中文说明](usage.zh-CN.md)* · [← Back to README](../README.md)

How to install Video2Text and use it from the command line, the desktop GUI, or the Chrome extension.

---

## Requirements

- **Python 3.12 or newer** — check your version by running `python3 --version`
- A terminal (Terminal on Mac, Command Prompt or PowerShell on Windows)
- An internet connection (to download subtitles and to call the AI provider's API)
- At least one **AI provider API key** — used to generate the summary, key points, and action items. See the provider table below. Without a key, the tool still works but produces simpler, pattern-matched notes.

The video must have subtitles available (either manually added or auto-generated). English and Chinese subtitles are supported.

---

## Setup

You only need to do this once.

**Step 1 — Download the project files**

If you have Git installed:

```bash
git clone <repository-url>
cd Video2Text
```

Or download the ZIP from the repository page and unzip it, then open a terminal in that folder.

**Step 2 — Create a virtual environment**

A virtual environment keeps the project's dependencies isolated from the rest of your system.

```bash
python3.12 -m venv .venv
```

You should now see a `.venv` folder inside the project directory.

**Step 3 — Activate the virtual environment**

On Mac or Linux:

```bash
source .venv/bin/activate
```

On Windows (Command Prompt):

```bash
.venv\Scripts\activate.bat
```

On Windows (PowerShell):

```bash
.venv\Scripts\Activate.ps1
```

Your terminal prompt will change to show `(.venv)` at the start — this means the environment is active.

**Step 4 — Install dependencies**

```bash
pip install -r requirements.txt
```

**Step 5 — Set an API key**

Set the `ANTHROPIC_API_KEY` environment variable to your API key from [console.anthropic.com](https://console.anthropic.com/).

On Mac or Linux:

```bash
export ANTHROPIC_API_KEY="your-key-here"
```

On Windows (Command Prompt):

```bash
set ANTHROPIC_API_KEY=your-key-here
```

On Windows (PowerShell):

```bash
$env:ANTHROPIC_API_KEY="your-key-here"
```

This only lasts for the current terminal session. To make it permanent, add the line to your shell's startup file (e.g. `~/.zshrc` or `~/.bashrc`) or your system's environment variables.

### Other AI providers (optional)

`ANTHROPIC_API_KEY` is the default, but several other providers are
supported too. Set any of these environment variables to make a provider
available. The CLI and desktop GUI automatically use whichever configured
provider comes first in the table below; the Chrome extension additionally
lets you pick one from a dropdown. If none are configured, or the selected
provider's call fails, the tool falls back to a pattern-matching heuristic:

| Provider | Environment variable |
|---|---|
| Claude (Anthropic) | `ANTHROPIC_API_KEY` |
| GPT (OpenAI) | `OPENAI_API_KEY` |
| Gemini (Google) | `GOOGLE_API_KEY` |
| 通义千问 Qwen (Alibaba) | `DASHSCOPE_API_KEY` |
| DeepSeek | `DEEPSEEK_API_KEY` |
| 豆包 Doubao (ByteDance) | `ARK_API_KEY` |
| Kimi (Moonshot) | `MOONSHOT_API_KEY` |
| 智谱 GLM (Zhipu) | `ZHIPU_API_KEY` |
| 文心一言 Ernie (Baidu) | `BAIDU_API_KEY` |
| Mistral | `MISTRAL_API_KEY` |

In the Chrome extension, the model dropdown shows a ✅ next to providers that
are configured and a 🔒 next to ones that aren't (yet).

---

## Usage (command line)

Make sure the virtual environment is active (you should see `(.venv)` in your prompt). Then run:

```bash
python main.py <youtube_url>
```

Replace `<youtube_url>` with any YouTube link. Both formats work:

```bash
python main.py https://www.youtube.com/watch?v=zjkBMFhNj_g
python main.py https://youtu.be/zjkBMFhNj_g
```

**Example output in the terminal:**

```
Reading video information...
Downloaded subtitles (en).
Generating transcript...
Generating notes with Claude...
Done.
Created output/transcript.txt
Created output/notes.md
```

Open the `output/` folder to find your files.

---

## Usage (desktop GUI)

```bash
python ui.py
```

Same idea as the CLI, with a window: paste a URL, pick a model from the
dropdown (only configured providers are listed), click Generate, browse the
Notes/Transcript tabs. Colors follow `app/theme.py` and automatically match
your OS's light/dark setting. The model list is read once at startup, so
restart the app after setting a new provider's API key.

---

## Usage (Chrome extension)

A browser-only panel embedded at the top of YouTube's sidebar. It reads the
current video's existing captions directly, with no Python process, local
server, API key, or cloud server.

**1. Load the extension in Chrome**

- Go to `chrome://extensions`
- Turn on "Developer mode" (top right)
- Click "Load unpacked" and select the `extension/` folder

**2. Use it**

Open a captioned YouTube video and click "提取现有字幕". You can copy the
transcript or download it as a TXT file. Videos without captions show a clear
message. The extension does not download audio, transcribe speech, or generate
AI notes. Its colors follow `extension/theme.css` and automatically match your
OS's light/dark setting.

---

## Output files

**`output/transcript.txt`**

The full spoken content of the video as clean, readable text. Timestamps and formatting codes from the subtitle file are removed, and it's automatically split into paragraphs (every few sentences) so it isn't a wall of one-line-per-caption text — this happens with or without an AI provider configured.

**`output/notes.md`**

A Markdown document structured as:

```
# Video Title

## Summary
A short paragraph written by the AI covering the main topic and conclusions.

## Key Points
- ...
- ...
- ...

## Action Items
- ...
- ...

## Transcript
The full transcript text.
```

You can open `.md` files in any text editor, or in apps like Obsidian, Notion, Typora, or VS Code for formatted rendering.

---

## Troubleshooting

**"No English or Chinese subtitles were found for this video."**

The video does not have subtitles available in a supported language. Try a different video, or one that has auto-generated captions enabled.

**"Invalid YouTube URL."**

Make sure you are passing a full URL, not just a video ID. The URL must start with `https://` and point to `youtube.com/watch?v=...` or `youtu.be/...`.

**"Could not read video information."**

The video may be private, age-restricted, or unavailable in your region. Try a different video.

**Notes look like plain sentences from the transcript (no AI summary)**

This means no provider's API key is set, or the API call failed. The tool falls back to simple pattern-matched notes so it can still finish. Check that you've set an environment variable from the provider table in Step 5 of Setup, and that the key is valid and has available credit.

**`python3.12` not found**

Install Python 3.12 from python.org. On Mac you can also use `brew install python@3.12`.

**The virtual environment is not active**

If you see errors about missing packages, run the activation command from Step 3 again. You need to activate the environment each time you open a new terminal window.

---

## Running tests

```bash
pytest
```
