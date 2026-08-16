# Constraints

## Purpose

This document defines the project goal, MVP scope, security constraints, technical constraints, coding style, and definition of success for Video Note Agent.

## Project Goal

The purpose of this project is:

### Input

- A YouTube video URL

### Output

- `transcript.txt`
- `notes.md`

The Notes should contain:

- Summary
- Key Points
- Action Items
- Clean Transcript

## MVP Scope

The MVP only supports:

- YouTube URLs
- Existing subtitles

The MVP does NOT support:

- Telegram Bot
- Discord Bot
- Feishu Bot
- Notion Integration
- Feishu Integration
- Docker
- Whisper
- Local LLM
- OpenAI API
- Multi-user support

## Security Constraints

The application must NOT:

- Read local user documents
- Read email accounts
- Read browser history
- Access Google Drive
- Access Notion
- Access Feishu
- Execute arbitrary shell commands

The application only processes:

- User supplied YouTube URLs
- Downloaded subtitles

## Technical Constraints

### Language

- Python 3.12+

Dependencies should be minimal.

### Preferred Libraries

- yt-dlp
- requests

### Avoid

- Heavy frameworks
- Complex databases

### Storage

- Local files only

No cloud services.

## Coding Style

### Requirements

- Simple structure
- Clear functions
- Readable code
- No over-engineering

The MVP should be understandable by a junior developer.

## Definition of Success

Running:

```bash
python main.py <youtube_url>
```

Should generate:

```text
output/transcript.txt
output/notes.md
```
