# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
make setup    # Create venv and install dependencies (first time)
make run      # Full pipeline: ingest → extract → report
make serve    # Start web server on port 8000
make update   # Run pipeline then start server
make ingest   # Only fetch new content
make extract  # Only run LLM extraction
make report   # Only generate markdown report
make clean    # Delete database and report.md
```

Individual pipeline steps can also be invoked directly:
```bash
python run.py                # Full pipeline
python run.py --ingest       # Ingest only
python run.py --extract      # Extract only
python run.py --report [N]   # Report only, N days lookback
```

Environment: set `GEMINI_API_KEY`, `DEEPSEEK_API_KEY`, or `ANTHROPIC_API_KEY` depending on the configured LLM provider.

## Architecture

The project is a single-pipeline Python application with no framework abstractions:

```
ingest.py → db.py → extract.py → db.py → report.py
                                       ↘ server.py (FastAPI, port 8000)
```

**`config.py`** — Central configuration: YouTube channel IDs, RSS feed URLs, LLM provider selection (`LLM_PROVIDER`), `LOOKBACK_DAYS`, `VIDEOS_PER_CHANNEL`, `MAX_TRANSCRIPT_LENGTH`, `DB_PATH`.

**`db.py`** — SQLite wrapper. Two tables: `sources` (raw ingested content, deduplicated by `url`) and `insights` (structured LLM output, FK to sources). Key functions: `insert_source()`, `insert_insights()`, `get_recent_insights(days)`, `source_exists(url)`.

**`ingest.py`** — Fetches YouTube transcripts (via YouTube RSS feed + `youtube-transcript-api`, no YouTube API key needed) and RSS feed entries. Skips URLs already in `sources` table. Returns list of new source IDs.

**`extract.py`** — Sends raw text to LLM and parses JSON response into structured insights: `category`, `model_or_tool`, `summary`, `significance`. Supports three providers with separate functions: `extract_insights_gemini()`, `extract_insights_deepseek()`, `extract_insights_anthropic()`. Temperature 0.1. Only processes sources that have no insights yet. Inserts a placeholder insight for sources with no AI content (marks them as processed to prevent re-extraction).

**`report.py`** — Queries insights from last N days, groups by category, sorts "major" significance first, outputs `report.md`.

**`server.py`** — FastAPI app. `GET /` renders all HTML/CSS/JS inline (no templates directory). `GET /api/insights?days=N` returns JSON. PWA-ready for iOS home screen installation.

**`run.py`** — Orchestrates the pipeline phases, handles CLI args.

## LLM Provider Configuration

Change `LLM_PROVIDER` in `config.py` to `"gemini"` (default), `"deepseek"`, or `"anthropic"`. The Anthropic provider uses Claude Haiku 4.5 (`claude-haiku-4-5-20251001`).

## Database

SQLite file at `DB_PATH` (default `ai_sota.db`). Deduplication is by `url` uniqueness in `sources`. Sources are only extracted once — if `insights` rows exist for a `source_id`, that source is skipped on future extract runs. Use `make clean` to reset everything.
