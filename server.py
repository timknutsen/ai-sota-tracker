#!/usr/bin/env python3
"""
Lightweight FastAPI server for AI SOTA Tracker.
Serves the report as a mobile-friendly PWA.

Usage:
    pip install fastapi uvicorn
    python server.py
    # Open http://your-server:8000 on your phone
    # Safari → Share → Add to Home Screen
"""
import os
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from db import init_db, get_db, get_recent_insights

app = FastAPI(title="AI SOTA Tracker")

CATEGORY_META = {
    "agentic_coding": ("🤖", "Agentic Coding"),
    "model_release":  ("🚀", "Model Releases"),
    "workflow":       ("⚡", "Workflows & Techniques"),
    "tool":           ("🔧", "Tools & Platforms"),
    "productivity":   ("💡", "Knowledge Work & Productivity"),
    "other":          ("📌", "Other"),
}

SIG_COLORS = {
    "major": "#ef4444",
    "minor": "#eab308",
    "incremental": "#94a3b8",
}


def build_html(days: int = 7) -> str:
    insights = get_recent_insights(days)

    # Group by category
    grouped: dict[str, list] = {}
    for ins in insights:
        cat = ins.get("category", "other")
        grouped.setdefault(cat, []).append(ins)

    # Count sources
    sources = set(i["source_name"] for i in insights)
    major = [i for i in insights if i.get("significance") == "major"]

    # Build insight cards HTML
    highlights_html = ""
    if major:
        cards = ""
        for ins in major:
            model = f"<strong>{ins['model_or_tool']}</strong> — " if ins.get("model_or_tool") else ""
            cards += f"""
            <div class="card major">
                <div class="card-body">{model}{ins['summary']}</div>
                <div class="card-source">
                    <a href="{ins['source_url']}">{ins['source_name']}</a>
                </div>
            </div>"""
        highlights_html = f"""
        <section>
            <h2>⚡ Key Highlights</h2>
            {cards}
        </section>"""

    sections_html = ""
    for cat in ["agentic_coding", "model_release", "workflow", "tool", "productivity", "other"]:
        items = grouped.get(cat, [])
        if not items:
            continue
        emoji, label = CATEGORY_META.get(cat, ("📌", cat))
        cards = ""
        for ins in items:
            sig = ins.get("significance", "incremental")
            color = SIG_COLORS.get(sig, "#94a3b8")
            model = f"<strong>{ins['model_or_tool']}</strong> — " if ins.get("model_or_tool") else ""
            cards += f"""
            <div class="card">
                <span class="sig-dot" style="background:{color}"></span>
                <div class="card-body">{model}{ins['summary']}</div>
                <div class="card-source">
                    <a href="{ins['source_url']}">{ins['source_name']}</a>
                </div>
            </div>"""
        sections_html += f"""
        <section>
            <h2>{emoji} {label}</h2>
            {cards}
        </section>"""

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    empty_msg = '<p class="empty">No insights found. Run the pipeline first: <code>python run.py</code></p>' if not insights else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="AI Tracker">
    <meta name="theme-color" content="#0f172a">
    <link rel="apple-touch-icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🤖</text></svg>">
    <title>AI SOTA Tracker</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro', system-ui, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            padding: env(safe-area-inset-top) 16px env(safe-area-inset-bottom);
            -webkit-font-smoothing: antialiased;
        }}

        header {{
            padding: 24px 0 16px;
            text-align: center;
            border-bottom: 1px solid #1e293b;
            margin-bottom: 20px;
        }}

        header h1 {{
            font-size: 22px;
            font-weight: 700;
            letter-spacing: -0.02em;
        }}

        header .meta {{
            font-size: 13px;
            color: #64748b;
            margin-top: 6px;
        }}

        .tabs {{
            display: flex;
            gap: 8px;
            margin-bottom: 20px;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            padding-bottom: 4px;
        }}

        .tab {{
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 500;
            white-space: nowrap;
            cursor: pointer;
            background: #1e293b;
            color: #94a3b8;
            border: none;
            transition: all 0.2s;
        }}

        .tab.active {{
            background: #3b82f6;
            color: #fff;
        }}

        section {{
            margin-bottom: 28px;
        }}

        section h2 {{
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 12px;
            color: #cbd5e1;
        }}

        .card {{
            background: #1e293b;
            border-radius: 12px;
            padding: 14px 16px;
            margin-bottom: 10px;
            position: relative;
            padding-left: 28px;
        }}

        .card.major {{
            border-left: 3px solid #ef4444;
            padding-left: 16px;
        }}

        .sig-dot {{
            position: absolute;
            left: 12px;
            top: 20px;
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }}

        .card-body {{
            font-size: 14px;
            line-height: 1.5;
            color: #e2e8f0;
        }}

        .card-body strong {{
            color: #60a5fa;
        }}

        .card-source {{
            margin-top: 8px;
            font-size: 12px;
        }}

        .card-source a {{
            color: #64748b;
            text-decoration: none;
        }}

        .legend {{
            display: flex;
            gap: 16px;
            font-size: 12px;
            color: #64748b;
            margin-bottom: 20px;
            padding: 0 4px;
        }}

        .legend span {{
            display: flex;
            align-items: center;
            gap: 4px;
        }}

        .legend .dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
        }}

        .empty {{
            text-align: center;
            color: #64748b;
            padding: 40px 0;
            font-size: 14px;
        }}

        code {{
            background: #1e293b;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 13px;
        }}

        footer {{
            text-align: center;
            padding: 20px 0;
            font-size: 12px;
            color: #475569;
        }}
    </style>
</head>
<body>
    <header>
        <h1>🤖 AI SOTA Tracker</h1>
        <div class="meta">{len(insights)} insights from {len(sources)} sources · last {days} days</div>
    </header>

    <div class="tabs" id="tabs">
        <button class="tab active" data-days="7">7 days</button>
        <button class="tab" data-days="14">14 days</button>
        <button class="tab" data-days="30">30 days</button>
    </div>

    <div class="legend">
        <span><div class="dot" style="background:#ef4444"></div> Major</span>
        <span><div class="dot" style="background:#eab308"></div> Minor</span>
        <span><div class="dot" style="background:#94a3b8"></div> Incremental</span>
    </div>

    {empty_msg}
    {highlights_html}
    {sections_html}

    <footer>Updated {now}</footer>

    <script>
        document.getElementById('tabs').addEventListener('click', e => {{
            if (e.target.classList.contains('tab')) {{
                const days = e.target.dataset.days;
                window.location.href = '/?days=' + days;
            }}
        }});
    </script>
</body>
</html>"""


@app.on_event("startup")
def startup():
    init_db()


@app.get("/", response_class=HTMLResponse)
async def index(days: int = 7):
    return build_html(days)


@app.get("/api/insights")
async def api_insights(days: int = 7):
    """JSON endpoint if you ever want to build a native app later."""
    return get_recent_insights(days)


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
