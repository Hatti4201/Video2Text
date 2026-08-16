# Implementation Plan

## Purpose

This document defines the implementation roadmap for Video Note Agent.

Each phase must be completed, validated, and accepted before moving to the next phase.

Future phases must not be implemented early unless explicitly approved.

---

# Project Vision

Build a self-hosted video note generation system that can:

1. Accept a video URL
2. Extract transcript content
3. Generate structured notes
4. Store knowledge in external systems
5. Eventually operate as a personal AI assistant

The project follows a local-first architecture and prioritizes simplicity, maintainability, and security.

---

# Phase 1 - MVP

## Goal

Generate notes from YouTube videos that already contain subtitles.

### Input

```text
YouTube URL
```

### Output

```text
output/transcript.txt
output/notes.md
```

### Included

- URL validation
- Subtitle detection
- Subtitle download
- Transcript generation
- Markdown note generation
- Error handling
- Unit tests

### Excluded

- Ollama
- Whisper
- OpenAI API
- Claude API
- Telegram
- Discord
- Feishu
- Notion
- Docker
- Web UI
- Authentication
- Multi-user support

### Success Criteria

See:

```text
docs/acceptance-criteria.md
```

### Status

- [ ] Not Started

---

# Phase 2 - Local LLM Note Generation

## Goal

Improve note quality using a local LLM.

### Input

```text
Transcript
```

### Output

```text
Enhanced notes.md
```

### Included

- Ollama integration
- Local model inference
- Structured summaries
- Better key points
- Better action items

### Excluded

- External AI APIs

### Candidate Models

```text
Qwen
DeepSeek Distill
Llama
```

### Status

- [ ] Not Started

---

# Phase 3 - Whisper Transcription

## Goal

Support videos without subtitles.

### Input

```text
Video URL
```

### Output

```text
Transcript generated from audio
```

### Included

- Audio download
- Audio extraction
- faster-whisper
- Transcript generation

### Workflow

```text
Has subtitles?
    Yes -> Use subtitles
    No  -> Run Whisper
```

### Status

- [ ] Not Started

---

# Phase 4 - Notion Integration

## Goal

Automatically publish notes to Notion.

### Included

- Notion API integration
- Automatic page creation
- Markdown-to-Notion conversion
- Return page URL

### Output

```text
Notion page link
```

### Status

- [ ] Not Started

---

# Phase 5 - Telegram Bot

## Goal

Allow remote usage through chat.

### Workflow

```text
User sends URL
    ↓
Bot receives message
    ↓
Video processed
    ↓
Notes generated
    ↓
Result returned
```

### Included

- Telegram Bot
- Task execution
- Status updates
- Result delivery

### Status

- [ ] Not Started

---

# Phase 6 - Docker Deployment

## Goal

Package the system for reproducible deployment.

### Included

- Dockerfile
- docker-compose
- Environment variables
- Volume mounting

### Benefits

- Easier deployment
- Easier migration
- Easier maintenance

### Status

- [ ] Not Started

---

# Phase 7 - Windows Home Server Deployment

## Goal

Deploy the system to the dedicated home workstation.

### Target Environment

```text
Windows 11
WSL2 Ubuntu
Docker
RTX 4070
```

### Included

- WSL2 setup
- Docker setup
- Local model deployment
- Long-running service configuration

### Status

- [ ] Not Started

---

# Phase 8 - Secure Remote Access

## Goal

Access the system outside the home network.

### Preferred Solutions

```text
Tailscale
ZeroTier
```

### Alternative

```text
Cloudflare Tunnel
```

### Not Recommended

```text
Direct public port forwarding
```

### Security Objectives

- No public exposure
- Encrypted access
- Controlled device access

### Status

- [ ] Not Started

---

# Phase 9 - Personal Knowledge System

## Goal

Expand beyond video processing.

### Potential Features

- PDF notes
- Podcast notes
- Web article notes
- Knowledge organization
- Daily digest generation

### Status

- [ ] Future

---

# Phase 10 - Personal Assistant Ecosystem

## Goal

Build a collection of specialized assistants.

### Recommended Architecture

```text
Video Agent
Document Agent
Calendar Agent
Email Agent
```

### Design Principle

Avoid a single agent with unrestricted access.

Use specialized agents with minimal permissions.

### Status

- [ ] Future

---

# Security Roadmap

## Phase 1

Restrictions:

- No local file access
- No account access
- No browser automation

## Phase 4+

Additional Controls:

- API key isolation
- Environment variables
- Access control

## Phase 7+

Additional Controls:

- Docker isolation
- Dedicated working directory
- Service separation

---

# Development Rules

All development must follow:

```text
docs/constraints.md
docs/prd.md
docs/todo.md
docs/folder-structure.md
docs/acceptance-criteria.md
```

Future phases must not be implemented before the current phase is completed and validated.

---

# Current Active Phase

```text
Phase 1 - MVP
```