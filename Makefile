.PHONY: setup run ingest extract report serve update clean

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PORT ?= 8000

# First time setup
setup:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo ""
	@echo "✅ Setup complete. Now run:"
	@echo "   export GEMINI_API_KEY='your-key-here'"
	@echo "   make run"

# Full pipeline: ingest → extract → report
run:
	$(PYTHON) run.py

# Individual steps
ingest:
	$(PYTHON) run.py --ingest

extract:
	$(PYTHON) run.py --extract

report:
	$(PYTHON) run.py --report

# Start web server
serve:
	$(PYTHON) server.py

# Full update + serve (the one you'll actually use)
update: run serve

# Nuke everything and start fresh
clean:
	rm -f ai_sota.db report.md
	@echo "✅ Database and report cleared"

# Show help
help:
	@echo "AI SOTA Tracker"
	@echo ""
	@echo "  make setup    — create venv and install deps (first time only)"
	@echo "  make run      — full pipeline: ingest → extract → report"
	@echo "  make serve    — start web server on port $(PORT)"
	@echo "  make update   — run pipeline then start server"
	@echo "  make ingest   — only fetch new content"
	@echo "  make extract  — only run LLM extraction"
	@echo "  make report   — only generate markdown report"
	@echo "  make clean    — delete database and report"
