# Acceptance Criteria

## Purpose

This document defines when the MVP is considered complete.

The project is NOT complete unless all criteria pass.

## AC-1 Project Setup

### Requirements

- Repository can be cloned successfully
- Python environment can be created
- Dependencies can be installed

### Verification

```bash
pip install -r requirements.txt
```

### Expected Result

- Installation completes successfully
- No dependency errors
- No manual fixes required

## AC-2 Command Line Execution

### Requirements

Application can be started from command line.

### Verification

```bash
python main.py <youtube_url>
```

### Expected Result

- Application starts successfully
- No crash
- User receives processing feedback

## AC-3 URL Validation

### Requirements

Application validates YouTube URLs.

### Verification

Valid URL:

```text
https://www.youtube.com/watch?v=example
```

Expected:

```text
Processing starts successfully
```

Invalid URL:

```text
hello-world
```

Expected:

```text
Readable error message
Application exits gracefully
```

## AC-4 Subtitle Retrieval

### Requirements

Application downloads subtitles.

### Verification

Input:

```text
YouTube video with subtitles
```

### Expected Result

- Subtitle file downloaded successfully
- No video file downloaded
- Subtitle language detected correctly

## AC-5 Transcript Generation

### Requirements

Application generates transcript.

### Verification

Output file:

```text
output/transcript.txt
```

### Expected Result

- Human-readable transcript
- No timestamps
- No subtitle metadata
- No empty content

## AC-6 Notes Generation

### Requirements

Application generates notes.

### Verification

Output file:

```text
output/notes.md
```

### Expected Result

The file contains:

```markdown
# Title

## Summary

## Key Points

## Action Items

## Transcript
```

All sections must exist.

## AC-7 Output Directory

### Requirements

Generated files are stored locally.

### Verification

Directory:

```text
output/
```

Files:

```text
output/transcript.txt
output/notes.md
```

### Expected Result

- Files are created successfully
- Files contain valid content

## AC-8 Error Handling

### Requirements

Application handles failures gracefully.

### Verification Cases

#### Invalid URL

Input:

```text
hello-world
```

Expected:

```text
Readable error message
No crash
```

#### Video Without Subtitles

Expected:

```text
Readable error message
No crash
```

#### Network Failure

Expected:

```text
Readable error message
No crash
```

## AC-9 Dependency Control

### Requirements

Use only necessary dependencies.

### Expected Result

Allowed examples:

```text
yt-dlp
requests
pytest
```

Avoid:

```text
postgresql
redis
rabbitmq
celery
django
fastapi
```

unless explicitly required by the MVP.

## AC-10 Code Structure

### Requirements

Project structure follows:

```text
docs/
app/
tests/
output/
```

### Expected Result

- No unnecessary directories
- No over-engineered architecture
- Clear separation of responsibilities

## AC-11 Test Coverage

### Requirements

Basic tests exist.

Required files:

```text
tests/test_downloader.py
tests/test_transcript.py
tests/test_notes.py
```

### Verification

```bash
pytest
```

### Expected Result

```text
All tests pass
```

## AC-12 End-to-End Validation

### Verification

```bash
python main.py <youtube_url>
```

### Expected Workflow

```text
1. Validate URL
2. Download subtitles
3. Generate transcript.txt
4. Generate notes.md
5. Save files into output/
6. Exit successfully
```

### Expected Result

```text
No crash
All output files generated
Workflow completes successfully
```

## MVP Success Checklist

The MVP is complete only when all items below are satisfied.

- [ ] Application accepts a YouTube URL
- [ ] Subtitles are downloaded successfully
- [ ] Transcript is generated successfully
- [ ] Notes are generated successfully
- [ ] Output files are created successfully
- [ ] Error handling works correctly
- [ ] All tests pass
- [ ] End-to-end workflow passes

## Final Definition of Done

The project is considered complete when:

```bash
python main.py <youtube_url>
```

successfully produces:

```text
output/transcript.txt
output/notes.md
```

and all acceptance criteria pass.
