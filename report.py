"""
Generate a markdown summary report from extracted insights.
"""
from datetime import datetime
from db import get_recent_insights

CATEGORY_LABELS = {
    "agentic_coding": "🤖 Agentic Coding",
    "model_release": "🚀 Model Releases",
    "workflow": "⚡ Workflows & Techniques",
    "tool": "🔧 Tools & Platforms",
    "productivity": "💡 Knowledge Work & Productivity",
    "other": "📌 Other",
}

SIGNIFICANCE_EMOJI = {
    "major": "🔴",
    "minor": "🟡",
    "incremental": "⚪",
}


def generate_report(days: int = 7) -> str:
    insights = get_recent_insights(days)
    
    if not insights:
        return f"# AI SOTA Tracker — {datetime.utcnow().strftime('%Y-%m-%d')}\n\nNo insights found for the last {days} days.\n"
    
    # Group by category
    grouped: dict[str, list] = {}
    for ins in insights:
        cat = ins.get("category", "other")
        grouped.setdefault(cat, []).append(ins)
    
    lines = [
        f"# AI SOTA Tracker — {datetime.utcnow().strftime('%Y-%m-%d')}",
        f"*Covering the last {days} days | {len(insights)} insights from {len(set(i['source_name'] for i in insights))} sources*\n",
    ]
    
    # Major highlights first
    major = [i for i in insights if i.get("significance") == "major"]
    if major:
        lines.append("## ⚡ Key Highlights\n")
        for ins in major:
            model = f"**{ins['model_or_tool']}**: " if ins.get("model_or_tool") else ""
            lines.append(f"- {model}{ins['summary']} *([{ins['source_name']}]({ins['source_url']}))*")
        lines.append("")
    
    # Then by category
    for cat in ["agentic_coding", "model_release", "workflow", "tool", "productivity", "other"]:
        items = grouped.get(cat, [])
        if not items:
            continue
        
        label = CATEGORY_LABELS.get(cat, cat)
        lines.append(f"## {label}\n")
        
        for ins in items:
            sig = SIGNIFICANCE_EMOJI.get(ins.get("significance", ""), "")
            model = f"**{ins['model_or_tool']}** — " if ins.get("model_or_tool") else ""
            lines.append(f"- {sig} {model}{ins['summary']}  ")
            lines.append(f"  *Source: [{ins['source_name']}]({ins['source_url']})*")
        
        lines.append("")
    
    lines.append("---")
    lines.append(f"*Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*\n")
    
    return "\n".join(lines)
