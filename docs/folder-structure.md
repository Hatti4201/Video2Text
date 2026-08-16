# Folder Structure

## Purpose

This document defines the expected folder structure, directory responsibilities, architecture rules, and maximum complexity rule for the Video Note Agent MVP.

## Project Structure

The MVP should use a simple and easy-to-understand structure.

Do not over-engineer.

```text
video-note-agent/
├── docs/
│   ├── constraints.md
│   ├── prd.md
│   ├── todo.md
│   ├── folder-structure.md
│   └── acceptance-criteria.md
│
├── app/
│   ├── downloader.py
│   ├── transcript.py
│   ├── notes.py
│   ├── utils.py
│   └── __init__.py
│
├── output/
│   ├── transcript.txt
│   └── notes.md
│
├── tests/
│   ├── test_downloader.py
│   ├── test_transcript.py
│   └── test_notes.py
│
├── main.py
│
├── requirements.txt
│
├── .gitignore
│
└── README.md
```

## Directory Responsibilities

### docs/

Contains project documentation.

No application code.

### app/

Contains all business logic.

#### downloader.py

Responsibilities:

- Validate YouTube URL
- Download subtitles
- Get video metadata

#### transcript.py

Responsibilities:

- Parse subtitle files
- Remove timestamps
- Generate transcript text

#### notes.py

Responsibilities:

- Generate markdown notes
- Create summary section
- Create key points section
- Create action items section

#### utils.py

Responsibilities:

- Shared helper functions

Keep this file small.

### output/

Contains generated files.

Generated at runtime.

Do not commit generated files.

### tests/

Contains unit tests.

One test file per module.

### main.py

Application entry point.

Expected usage:

```bash
python main.py <youtube_url>
```

### requirements.txt

Contains project dependencies.

Keep dependencies minimal.

## Architecture Rules

The MVP must remain:

- Simple
- Local-first
- Single-user
- CLI-based

Avoid:

- Databases
- Web frameworks
- Authentication
- Background workers
- Message queues
- Cloud services

## Maximum Complexity Rule

If a feature can be implemented in:

```text
1 file
```

do not create:

```text
3 files
```

If a function can be:

```text
20 lines
```

do not create:

```text
5 classes
```

Keep the MVP small.
