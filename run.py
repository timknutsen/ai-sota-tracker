#!/usr/bin/env python3
"""
AI SOTA Tracker — main pipeline
Usage:
    python run.py              # Full pipeline: ingest → extract → report
    python run.py --ingest     # Only ingest new content
    python run.py --extract    # Only extract insights from un-processed sources
    python run.py --report     # Only generate report
    python run.py --report 14  # Report for last 14 days
"""
import sys
from db import init_db, get_db, insert_insights
from ingest import ingest_all
from extract import extract_insights
from report import generate_report


def run_ingest() -> list[int]:
    print("\n🔄 INGESTING SOURCES...")
    return ingest_all()


def run_extract(source_ids: list[int] | None = None):
    """Extract insights from sources. If source_ids is None, process all un-extracted sources."""
    conn = get_db()
    
    if source_ids:
        # Process specific sources
        rows = conn.execute(
            f"SELECT id, title, raw_text FROM sources WHERE id IN ({','.join('?' * len(source_ids))})",
            source_ids
        ).fetchall()
    else:
        # Process sources that have no insights yet
        rows = conn.execute("""
            SELECT s.id, s.title, s.raw_text
            FROM sources s
            LEFT JOIN insights i ON s.id = i.source_id
            WHERE i.id IS NULL AND s.raw_text IS NOT NULL
        """).fetchall()
    
    conn.close()
    
    if not rows:
        print("No sources to process")
        return
    
    print(f"\n🧠 EXTRACTING INSIGHTS FROM {len(rows)} SOURCES...")
    
    total_insights = 0
    for row in rows:
        title = row["title"][:60]
        print(f"\n  🔍 Processing: {title}")
        
        try:
            insights = extract_insights(row["raw_text"])
            if insights:
                insert_insights(row["id"], insights)
                print(f"     → {len(insights)} insights extracted")
                total_insights += len(insights)
            else:
                # Insert a placeholder so we don't reprocess
                insert_insights(row["id"], [{"summary": "No AI insights found", "category": "other", "significance": "incremental"}])
                print(f"     → No relevant insights")
        except Exception as e:
            print(f"     ⚠ Error: {e}")
    
    print(f"\n✅ Extracted {total_insights} insights total")


def run_report(days: int = 7):
    print(f"\n📋 GENERATING REPORT (last {days} days)...")
    md = generate_report(days)
    
    filename = "report.md"
    with open(filename, "w") as f:
        f.write(md)
    
    print(f"✅ Report saved to {filename}")
    print("\n" + "=" * 60)
    print(md)


def main():
    init_db()
    
    args = sys.argv[1:]
    
    if not args:
        # Full pipeline
        source_ids = run_ingest()
        run_extract(source_ids)
        run_report()
    elif "--ingest" in args:
        run_ingest()
    elif "--extract" in args:
        run_extract()
    elif "--report" in args:
        days = 7
        # Check if a number follows --report
        idx = args.index("--report")
        if idx + 1 < len(args) and args[idx + 1].isdigit():
            days = int(args[idx + 1])
        run_report(days)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
