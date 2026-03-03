"""
Ingest content from YouTube (via transcripts) and RSS feeds.
"""
import re
import json
import requests
import feedparser
import trafilatura
from datetime import datetime, timedelta
from youtube_transcript_api import YouTubeTranscriptApi

from config import (
    YOUTUBE_CHANNELS, RSS_FEEDS, VIDEOS_PER_CHANNEL,
    MAX_TRANSCRIPT_LENGTH, LOOKBACK_DAYS
)
from db import source_exists, insert_source


# ---------------------------------------------------------------------------
# YouTube
# ---------------------------------------------------------------------------

def get_recent_video_ids(channel_id: str, max_results: int = 5) -> list[dict]:
    """
    Fetch recent video IDs from a channel using the RSS feed trick
    (no API key needed).
    """
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    feed = feedparser.parse(feed_url)
    
    cutoff = datetime.utcnow() - timedelta(days=LOOKBACK_DAYS)
    videos = []
    
    for entry in feed.entries[:max_results]:
        published = datetime(*entry.published_parsed[:6])
        if published < cutoff:
            continue
        
        video_id = entry.yt_videoid
        videos.append({
            "video_id": video_id,
            "title": entry.title,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "published_at": published.isoformat(),
        })
    
    return videos


def get_transcript(video_id: str) -> str | None:
    """Fetch transcript for a video. Returns None if unavailable."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join(seg["text"] for seg in transcript)
        # Truncate if too long
        if len(text) > MAX_TRANSCRIPT_LENGTH:
            text = text[:MAX_TRANSCRIPT_LENGTH] + "\n\n[TRUNCATED]"
        return text
    except Exception as e:
        print(f"  ⚠ No transcript for {video_id}: {e}")
        return None


def ingest_youtube() -> list[int]:
    """Ingest recent YouTube videos. Returns list of new source IDs."""
    source_ids = []
    
    for channel in YOUTUBE_CHANNELS:
        print(f"\n📺 {channel['name']}")
        videos = get_recent_video_ids(channel["channel_id"], VIDEOS_PER_CHANNEL)
        
        if not videos:
            print("  No recent videos found")
            continue
        
        for vid in videos:
            if source_exists(vid["url"]):
                print(f"  ⏭ Already ingested: {vid['title'][:60]}")
                continue
            
            print(f"  📝 Fetching transcript: {vid['title'][:60]}")
            transcript = get_transcript(vid["video_id"])
            
            if transcript:
                sid = insert_source(
                    source_type="youtube",
                    source_name=channel["name"],
                    title=vid["title"],
                    url=vid["url"],
                    published_at=vid["published_at"],
                    raw_text=transcript,
                )
                source_ids.append(sid)
    
    return source_ids


# ---------------------------------------------------------------------------
# RSS Feeds
# ---------------------------------------------------------------------------

def clean_html(text: str) -> str:
    """Strip HTML tags from RSS content."""
    return re.sub(r"<[^>]+>", "", text or "")


def fetch_full_article(url: str) -> str | None:
    """
    Fetch the full article at `url` and return clean markdown text.
    Uses trafilatura for boilerplate removal (nav, ads, footers).
    Returns None if the page can't be fetched or extracted.
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return None
        text = trafilatura.extract(
            downloaded,
            output_format="markdown",
            include_links=False,
            include_images=False,
        )
        return text or None
    except Exception:
        return None


def ingest_rss() -> list[int]:
    """Ingest recent RSS feed entries. Returns list of new source IDs."""
    source_ids = []
    cutoff = datetime.utcnow() - timedelta(days=LOOKBACK_DAYS)
    
    for feed_cfg in RSS_FEEDS:
        print(f"\n📰 {feed_cfg['name']}")
        
        try:
            feed = feedparser.parse(feed_cfg["url"])
        except Exception as e:
            print(f"  ⚠ Failed to parse feed: {e}")
            continue
        
        for entry in feed.entries[:5]:
            # Parse date
            published = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6])
                if published < cutoff:
                    continue
            
            url = entry.get("link", "")
            if not url or source_exists(url):
                continue
            
            # Try fetching the full article first; fall back to feed summary
            raw = fetch_full_article(url)
            if raw:
                print(f"    (full article fetched, {len(raw)} chars)")
            else:
                raw = clean_html(
                    entry.get("content", [{}])[0].get("value", "")
                    if entry.get("content")
                    else entry.get("summary", "")
                )

            if not raw or len(raw) < 100:
                print(f"  ⏭ Skipping (too short): {entry.get('title', '?')[:60]}")
                continue

            if len(raw) > MAX_TRANSCRIPT_LENGTH:
                raw = raw[:MAX_TRANSCRIPT_LENGTH] + "\n\n[TRUNCATED]"
            
            print(f"  📝 Ingested: {entry.get('title', '?')[:60]}")
            sid = insert_source(
                source_type="rss",
                source_name=feed_cfg["name"],
                title=entry.get("title", "Untitled"),
                url=url,
                published_at=published.isoformat() if published else None,
                raw_text=raw,
            )
            source_ids.append(sid)
    
    return source_ids


def ingest_all() -> list[int]:
    """Run all ingestion. Returns list of new source IDs."""
    print("=" * 60)
    print("INGESTING YOUTUBE")
    print("=" * 60)
    yt_ids = ingest_youtube()
    
    print("\n" + "=" * 60)
    print("INGESTING RSS FEEDS")
    print("=" * 60)
    rss_ids = ingest_rss()
    
    all_ids = yt_ids + rss_ids
    print(f"\n✅ Ingested {len(all_ids)} new sources")
    return all_ids
