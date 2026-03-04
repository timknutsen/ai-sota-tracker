# AI SOTA Tracker

A lightweight pipeline that ingests content from trusted AI sources (YouTube transcripts + RSS feeds), extracts structured insights using an LLM, and generates a weekly markdown summary of what's new in AI.

## Setup

```bash
# Create venv and install dependencies
make setup

# Set your LLM API key (pick one)
export GEMINI_API_KEY="your-key-here"       # default provider
# export DEEPSEEK_API_KEY="your-key-here"   # alternative
# export ANTHROPIC_API_KEY="your-key-here"  # alternative
```

## Usage

### Make commands (recommended)

```bash
make run      # Full pipeline: ingest → extract → report
make serve    # Start web server on port 8000
make update   # Run pipeline then start server
make ingest   # Only fetch new content
make extract  # Only run LLM extraction
make report   # Only generate markdown report
make clean    # Delete database and report.md
```

### Direct invocation

```bash
python run.py                # Full pipeline
python run.py --ingest       # Fetch new content only
python run.py --extract      # Run LLM extraction on new content only
python run.py --report       # Generate markdown report (last 7 days)
python run.py --report 14    # Report for last 14 days
```

## Configuration

Edit `config.py` to:
- Add/remove YouTube channels and RSS feeds
- Switch LLM provider (`gemini`, `deepseek`, `anthropic`)
- Adjust lookback window (`LOOKBACK_DAYS`), videos per channel, transcript length limits

### Default sources

**YouTube channels:**
- Andrej Karpathy, AI Explained, Jeremy Howard
- AI Jason, McKay Wrigley, Fireship, Matt Shumer

**RSS feeds:**
- Simon Willison, Latent Space, Ethan Mollick (One Useful Thing), Stratechery, ThursdAI
- Anthropic Blog, OpenAI Blog, Google DeepMind Blog

### LLM providers

| Provider | Env var | Model |
|---|---|---|
| `gemini` (default) | `GEMINI_API_KEY` | Gemini |
| `deepseek` | `DEEPSEEK_API_KEY` | DeepSeek |
| `anthropic` | `ANTHROPIC_API_KEY` | Claude Haiku 4.5 |

## Automate with cron

Run weekly on Sunday at 8am:
```
0 8 * * 0 cd /path/to/ai-sota-tracker && make run >> run.log 2>&1
```

## Mobile app (PWA)

The server gives you a mobile-friendly web app you can add to your iPhone home screen.

```bash
make serve           # Start on port 8000
PORT=9000 make serve # Custom port
```

Then on your iPhone:
1. Open Safari → `http://your-server-ip:8000`
2. Tap **Share** → **Add to Home Screen**
3. It now looks and behaves like a native app

The server also exposes a JSON API at `/api/insights?days=7`.

**Tip:** If running on AWS, make sure port 8000 is open in your security group. For HTTPS (recommended), put it behind Caddy or nginx with a Let's Encrypt cert.

## Project structure

```
config.py    — sources list, LLM settings
db.py        — SQLite storage layer
ingest.py    — YouTube transcript + RSS feed ingestion
extract.py   — LLM-based structured extraction
report.py    — Markdown report generator
run.py       — Main pipeline runner
server.py    — FastAPI web server (PWA)
```
