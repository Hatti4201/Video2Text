# PRD

## Purpose

This Product Requirements Document defines the goals, scope, requirements, roadmap, and success criteria for Video Note Agent.

## Project Name

Video Note Agent

## Overview

Video Note Agent is a self-hosted personal tool that converts video content into structured notes.

The user provides a video source.

The system automatically:

1. Retrieves subtitles or transcript content
2. Extracts transcript
3. Cleans transcript
4. Generates structured notes
5. Saves results as local files

The goal is to help users efficiently consume educational and informational content.

## Problem Statement

Many valuable videos contain useful information but are difficult to review later.

Users often:

- Watch long videos
- Forget important points
- Need searchable notes
- Need a clean transcript
- Need structured summaries

Manually creating notes is time-consuming.

The system should automate this process.

## Target User

Primary User:

- Single user
- Personal usage
- Technical background
- Uses online and local video content for learning

Current version is not intended for public users.

## MVP Goal

### Input

A YouTube video URL

### Output

```text
output/transcript.txt
output/notes.md
```

Generated notes should be readable and organized.

## User Flow

User runs:

```bash
python main.py <youtube_url>
```

Workflow:

1. System downloads subtitles
2. System extracts transcript
3. System cleans transcript
4. System generates notes
5. System saves files
6. User reads results

## Functional Requirements

### FR-1 Video Source Input

The system must accept:

- YouTube URL

Example:

```text
https://www.youtube.com/watch?v=xxxx
```

### FR-2 Subtitle Retrieval

The system should:

- Detect available subtitles
- Download subtitles

Supported:

- English subtitles
- Chinese subtitles

If subtitles are unavailable:

Return an error message.

### FR-3 Transcript Generation

The system must create:

```text
output/transcript.txt
```

Requirements:

- Plain text
- Human readable
- No timestamps
- No subtitle metadata

### FR-4 Note Generation

The system must create:

```text
output/notes.md
```

Required Sections:

```markdown
# Title

## Summary

## Key Points

## Action Items

## Transcript
```

### FR-5 Output Storage

All outputs must be stored locally.

Directory:

```text
output/
```

Files:

```text
transcript.txt
notes.md
```

## Non-Functional Requirements

### Simplicity

The MVP should remain small and easy to understand.

### Local-First

No cloud services.

No external databases.

### Maintainability

Code should be organized into small modules.

Avoid unnecessary abstractions.

### Security

Only process user-provided video sources.

Do not access personal files outside the project workspace.

Do not access email accounts.

Do not access cloud storage accounts.

Do not execute arbitrary commands.

## Out of Scope

The following are explicitly excluded from MVP:

- Local video files
- Whisper
- Ollama
- Local LLM
- OpenAI API
- Claude API
- Telegram Bot
- Discord Bot
- Feishu Bot
- Notion Integration
- Docker
- Web UI
- Authentication
- Multi-user support

## Future Roadmap

### Phase 2 - Local LLM Notes

- Ollama integration
- Local LLM support
- Improved note quality
- Better summaries
- Better action items

### Phase 3 - Local Video Support and Whisper

Additional Inputs:

```text
.mp4
.mov
.mkv
```

Features:

- Audio extraction
- Whisper transcription
- Transcript generation without subtitles

Workflow:

```text
Video Source
    ↓
Subtitle Available?
    ↓
Yes → Use Subtitle
No  → Use Whisper
```

### Phase 4 - Notion Integration

- Create Notion pages automatically
- Store generated notes
- Return page URL

### Phase 5 - Telegram Bot

- Remote chat interface
- URL submission
- Status notifications
- Result delivery

### Phase 6 - Docker Deployment

- Dockerfile
- docker-compose
- Environment management

### Phase 7 - Windows Home Server Deployment

- WSL2 deployment
- Local model deployment
- Long-running service setup

### Phase 8 - Secure Remote Access

- Tailscale
- ZeroTier
- Cloudflare Tunnel

### Phase 9 - Personal Knowledge System

Additional Inputs:

```text
PDF
Podcast
Web Article
Meeting Recording
```

Additional Outputs:

```text
Knowledge Base
Daily Digest
Topic Collections
```

### Phase 10 - Personal Assistant Ecosystem

Specialized Agents:

```text
Video Agent
Document Agent
Calendar Agent
Email Agent
```

## Success Criteria

The project is successful when:

### Input

```bash
python main.py <youtube_url>
```

### Output

```text
output/transcript.txt
output/notes.md
```

Both files are generated successfully and contain useful content.

The workflow completes without manual intervention.

The generated notes are readable, organized, and useful for future reference.