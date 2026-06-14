"""Configuration and constants for the gaming news bot."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Discord Configuration
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
if not DISCORD_WEBHOOK_URL:
    raise ValueError("DISCORD_WEBHOOK_URL environment variable is required")

# YouTube Configuration
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
if not YOUTUBE_API_KEY:
    raise ValueError("YOUTUBE_API_KEY environment variable is required")

# Games Configuration
GAMES = {
    "cs2": {
        "name": "Counter-Strike 2",
        "keywords": ["counter-strike 2", "cs2", "csgo", "counter-strike"],
        "youtube_queries": [
            "CS2 news 2026",
            "CS2 update patch notes",
            "CS2 guide 2026",
            "CS2 pro match highlights",
            "CS2 tips tricks 2026",
            "CS2 tournament 2026",
        ],
        "subreddits": ["GlobalOffensive", "cs2"],
        "official_sources": ["Valve", "Counter-Strike", "CS2"],
    }
}

# Reddit Configuration
REDDIT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
REDDIT_REQUEST_DELAY = 2  # seconds between requests
REDDIT_TIMEOUT = 10  # seconds

# YouTube Configuration
YOUTUBE_MAX_RESULTS = 10
YOUTUBE_SEARCH_DAYS = 7  # Search for videos from last N days
YOUTUBE_RELEVANT_CHANNELS = [
    "ESL Counter-Strike", "BLAST Premier", "Counter-Strike",
    "HLTV", "3kliksphilip", "BananaGaming", "NaVi", "FaZe Clan",
    "ProGuides CS2", "Valve"
]

# News Sites RSS Feeds
NEWS_RSS_FEEDS = {
    "hltv": "https://www.hltv.org/rss/news",
    "dotesports": "https://dotesports.com/feed",
    "pcgamer": "https://www.pcgamer.com/rss/",
    "polygon": "https://www.polygon.com/rss/index.xml",
    "vg247": "https://www.vg247.com/feed",
    "eurogamer": "https://www.eurogamer.net/?format=rss",
}

# Content Prioritization
PRIORITY_WEIGHTS = {
    "official": 100,      # Official announcements, patches
    "major_news": 75,     # Reviews, previews, interviews
    "community": 50,      # Viral clips, discoveries
    "discussion": 25,     # Opinion pieces, analysis
}

# Content filtering
MAX_CONTENT_AGE_DAYS = 7  # Don't include content older than this
PREFERRED_CONTENT_AGE_HOURS = 24  # Prefer content from last 24 hours
FALLBACK_CONTENT_AGE_HOURS = 72  # Fallback to 72 hours if not enough content
ITEMS_PER_GAME = 15  # Number of items to include per game

# Source distribution (15 items, YouTube ~50%)
SOURCE_DISTRIBUTION = {
    "news": (3, 5),      # 3-5 news articles
    "reddit": (3, 4),    # 3-4 Reddit posts
    "youtube": (7, 8),   # 7-8 YouTube videos (~50%)
}

# Games to exclude from trending news section
EXCLUDED_GAMES = ["fortnite", "battlefield", "arc raiders"]

# YouTube videos containing these words are filtered out
YOUTUBE_BLOCKED_KEYWORDS = [
    "hack", "cheat", "aimbot", "esp", "wallhack", "spinbot",
    "bypass", "undetected", "free hack", "keydrop", "promo code",
    "skin gambling", "case opening", "skin changer",
]

# Content Type Emojis
CONTENT_EMOJIS = {
    "official": "🔥",
    "news": "📰",
    "video": "🎬",
    "discussion": "💬",
    "analysis": "📊",
}

# Timezone Configuration
TIMEZONE = "US/Pacific"  # PST/PDT with automatic DST handling
TARGET_HOUR_PST = 14  # 2 PM PST

# Error Handling
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds
REQUEST_TIMEOUT = 30  # seconds

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
