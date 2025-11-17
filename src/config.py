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
    "battlefield6": {
        "name": "Battlefield 6",
        "keywords": ["battlefield 6", "battlefield6", "bf6", "battlefield 2042"],
        "subreddits": ["battlefield", "Battlefield6"],
        "official_sources": ["EA", "DICE", "Battlefield"],
    },
    "arcraiders": {
        "name": "Arc Raiders",
        "keywords": ["arc raiders", "arcraiders"],
        "subreddits": ["arcraiders"],
        "official_sources": ["Embark Studios", "Arc Raiders"],
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
    "IGN", "GameSpot", "Eurogamer", "PC Gamer", "Polygon",
    "VG247", "Battlefield", "Embark Studios"
]

# News Sites RSS Feeds
NEWS_RSS_FEEDS = {
    "ign": "https://feeds.ign.com/ign/all",
    "kotaku": "https://kotaku.com/rss",
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
ITEMS_PER_GAME = 5  # Number of items to include per game

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
