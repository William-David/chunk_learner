# Chunk Learner

A Python learning project that helps you break down your learning journey into manageable chunks with dependencies and difficulty levels.

## What is this?

Chunk Learner is a CLI tool (eventually a web app) for managing learning tasks. Define your own "chunks" of knowledge to learn, set their difficulty, and create dependencies between them (e.g., "Learn Pandas" before "Build ML Model").

## Setup

### Prerequisites
- Python 3.14
- pyenv (for managing Python versions)

### Installation

1. Create a virtual environment:
```bash
python3.14 -m venv .venv
```

2. Activate the virtual environment:
```bash
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install the package in development mode:
```bash
pip install -e .
```

### Usage

Initialize the database:
```bash
chunk-learner init
```

Add a new learning chunk:
```bash
chunk-learner add
```

List all chunks:
```bash
chunk-learner list
```

Get the next chunk to work on:
```bash
chunk-learner next
```

Mark a chunk as complete:
```bash
chunk-learner complete <chunk-id>
```

## Project Structure

- `src/chunk_learner/` - Main application code
  - `cli.py` - CLI commands and user interaction
  - `database.py` - Database connection and schema
  - `operations.py` - Business logic (CRUD operations)
  - `models.py` - Data models
- `data/` - SQLite database storage
- `tests/` - Test suite

## Roadmap

- [x] CLI with basic commands
- [ ] SQLite database with dependency tracking
- [ ] Reward system for chunk completion
- [ ] Key/unlock mechanism for advanced chunks
- [ ] FastAPI backend
- [ ] Web frontend

## Learning Goals

This project is designed to help me learn:
- Python fundamentals
- Database design and SQLite
- CLI development with Typer
- Testing with pytest
- API development with FastAPI
- Software engineering best practices
