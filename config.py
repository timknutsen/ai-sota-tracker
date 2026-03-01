"""
Configuration for AI SOTA Tracker
Focus: Agentic coding, work automation, AI for knowledge work.
"""

# --- YouTube Channels ---
# Format: {"name": display_name, "channel_id": youtube_channel_id}
YOUTUBE_CHANNELS = [
    # Big picture / fundamentals
    {"name": "Andrej Karpathy", "channel_id": "UCXUPKJO5MZQN11PqgIvyuvQ"},
    {"name": "AI Explained", "channel_id": "UCNJ1Ymd5yFuUPtn21xtRbbw"},
    {"name": "Jeremy Howard", "channel_id": "UCX7Y2qWriXpqocG97SFW2OQ"},

    # Agentic coding & AI tools
    {"name": "AI Jason", "channel_id": "UCfpdmMqHhRBmTgTHZakiRhg"},
    {"name": "McKay Wrigley", "channel_id": "UCvXfJKgDJLYBFnYMGsOOoNg"},
    {"name": "Fireship", "channel_id": "UCsBjURrPoezykLs9EqgamOA"},
    {"name": "Matt Shumer", "channel_id": "UCi3VCaFA2XcQNq4co3sYwDQ"},
]

# --- RSS Feeds ---
RSS_FEEDS = [
    # Practical AI tooling & agentic coding
    {"name": "Simon Willison", "url": "https://simonwillison.net/atom/everything/"},
    {"name": "Latent Space", "url": "https://www.latent.space/feed"},
    {"name": "Ethan Mollick (One Useful Thing)", "url": "https://www.oneusefulthing.org/feed"},
    {"name": "Stratechery", "url": "https://stratechery.com/feed/"},
    {"name": "ThursdAI", "url": "https://thursdai.news/feed"},

    # Official model/tool releases (only the big ones matter)
    {"name": "Anthropic Blog", "url": "https://www.anthropic.com/rss.xml"},
    {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml"},
    {"name": "Google DeepMind Blog", "url": "https://deepmind.google/blog/rss.xml"},
]

# --- LLM Settings ---
LLM_PROVIDER = "gemini"  # "gemini", "deepseek", or "anthropic"

# API keys — set as environment variables:
# GEMINI_API_KEY, DEEPSEEK_API_KEY, or ANTHROPIC_API_KEY

# --- Database ---
DB_PATH = "ai_sota.db"

# --- Ingestion settings ---
VIDEOS_PER_CHANNEL = 5
MAX_TRANSCRIPT_LENGTH = 30000
LOOKBACK_DAYS = 7
