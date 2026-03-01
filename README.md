# AI SOTA Tracker

A lightweight pipeline that ingests content from trusted AI sources (YouTube transcripts + RSS feeds), extracts structured insights using an LLM, and generates a weekly markdown summary of what's new in AI.

## Setup

```bash
pip install -r requirements.txt

# Set your LLM API key (pick one)
export GEMINI_API_KEY="your-key-here"       # default provider
# export DEEPSEEK_API_KEY="your-key-here"   # alternative
# export ANTHROPIC_API_KEY="your-key-here"  # alternative
```

## Usage

```bash
# Full pipeline: ingest → extract → report
python run.py

# Individual steps
python run.py --ingest       # fetch new content
python run.py --extract      # run LLM extraction on new content
python run.py --report       # generate markdown report (last 7 days)
python run.py --report 14    # report for last 14 days
```

## Configuration

Edit `config.py` to:
- Add/remove YouTube channels and RSS feeds
- Switch LLM provider (`gemini`, `deepseek`, `anthropic`)
- Adjust lookback window, transcript length limits

## Automate with cron

Run weekly on Sunday at 8am:
```
0 8 * * 0 cd /path/to/ai-sota-tracker && python run.py >> run.log 2>&1
```

## Mobile app (PWA)

The server gives you a mobile-friendly web app you can add to your iPhone home screen.

```bash
# Start the server (on your AWS instance or any machine)
python server.py

# Or with a custom port
PORT=9000 python server.py
```

Then on your iPhone:
1. Open Safari → `http://your-server-ip:8000`
2. Tap **Share** → **Add to Home Screen**
3. It now looks and behaves like a native app

The server also exposes a JSON API at `/api/insights?days=7` if you ever want to build a native frontend later.

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
