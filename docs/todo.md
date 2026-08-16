# MVP Development Tasks

## Purpose

This document tracks the implementation checklist for the Video Note Agent MVP.

## Phase 1 - Project Setup

### Task 1

Create project structure.

Required:

- `app/`
- `output/`
- `tests/`
- `docs/`

Status:

- [ ] Not Started

### Task 2

Create Python virtual environment instructions.

Required:

- Python 3.12+
- `requirements.txt`

Status:

- [ ] Not Started

### Task 3

Create main entry point.

File:

```text
main.py
```

Requirements:

Accept:

```bash
python main.py <youtube_url>
```

Status:

- [ ] Not Started

## Phase 2 - Subtitle Download

### Task 4

Install and configure yt-dlp.

Requirements:

- Download subtitles only
- Do not download video

Status:

- [ ] Not Started

### Task 5

Detect subtitle language.

Supported:

- English
- Chinese

Status:

- [ ] Not Started

### Task 6

Download subtitles.

Output:

```text
output/raw_subtitle.vtt
```

Status:

- [ ] Not Started

## Phase 3 - Transcript Generation

### Task 7

Parse subtitle file.

Requirements:

Remove:

- timestamps
- subtitle numbering
- metadata

Status:

- [ ] Not Started

### Task 8

Generate transcript.

Output:

```text
output/transcript.txt
```

Status:

- [ ] Not Started

## Phase 4 - Note Generation

### Task 9

Extract title.

Requirements:

Use video title as note title.

Status:

- [ ] Not Started

### Task 10

Generate summary.

Requirements:

Simple rule-based summary.

No LLM.

Status:

- [ ] Not Started

### Task 11

Generate key points.

Requirements:

At least 3 bullet points.

Status:

- [ ] Not Started

### Task 12

Generate action items.

Requirements:

Extract actionable content when possible.

Status:

- [ ] Not Started

### Task 13

Generate markdown document.

Output:

```text
output/notes.md
```

Template:

```markdown
# Title

## Summary

## Key Points

## Action Items

## Transcript
```

Status:

- [ ] Not Started

## Phase 5 - Error Handling

### Task 14

Handle invalid URLs.

Requirements:

Display readable error message.

Status:

- [ ] Not Started

### Task 15

Handle videos without subtitles.

Requirements:

Display readable error message.

Status:

- [ ] Not Started

### Task 16

Handle download failures.

Requirements:

Gracefully exit.

Status:

- [ ] Not Started

## Phase 6 - Testing

### Task 17

Create basic tests.

Requirements:

Test:

- URL validation
- Subtitle parsing
- Transcript generation

Status:

- [ ] Not Started

### Task 18

End-to-end test.

Input:

```text
YouTube URL
```

Output:

```text
transcript.txt
notes.md
```

Status:

- [ ] Not Started

## MVP Completion Checklist

Project is complete when:

- [ ] User can provide YouTube URL
- [ ] Subtitles can be downloaded
- [ ] Transcript can be generated
- [ ] Notes can be generated
- [ ] notes.md is readable
- [ ] transcript.txt is readable
- [ ] Error handling works
- [ ] Tests pass
