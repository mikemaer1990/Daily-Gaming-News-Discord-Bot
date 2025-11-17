"""News aggregator using RSS feeds from gaming news sites."""
import feedparser
import logging
from datetime import datetime, timedelta
from typing import List, Dict

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import NEWS_RSS_FEEDS, MAX_CONTENT_AGE_DAYS

logger = logging.getLogger(__name__)


class NewsAggregator:
    """Aggregates news articles from gaming news sites via RSS feeds."""

    def __init__(self):
        self.feeds = NEWS_RSS_FEEDS

    def fetch_feed(self, feed_name: str, feed_url: str, keywords: List[str]) -> List[Dict]:
        """
        Fetch and filter articles from a single RSS feed.

        Args:
            feed_name: Name of the news source
            feed_url: URL of the RSS feed
            keywords: List of keywords to filter articles

        Returns:
            List of relevant articles
        """
        try:
            logger.info(f"Fetching RSS feed from {feed_name}")
            feed = feedparser.parse(feed_url)

            articles = []
            cutoff_date = datetime.utcnow() - timedelta(days=MAX_CONTENT_AGE_DAYS)

            for entry in feed.entries:
                try:
                    # Parse timestamp
                    timestamp = None
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        timestamp = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                        timestamp = datetime(*entry.updated_parsed[:6])
                    else:
                        # If no timestamp, assume recent
                        timestamp = datetime.utcnow()

                    # Filter by age
                    if timestamp < cutoff_date:
                        continue

                    # Filter by keywords
                    title = entry.title.lower()
                    description = entry.get("summary", "").lower()
                    content = f"{title} {description}"

                    if not any(keyword.lower() in content for keyword in keywords):
                        continue

                    # Extract thumbnail if available
                    thumbnail = None
                    if hasattr(entry, "media_content") and entry.media_content:
                        thumbnail = entry.media_content[0].get("url")
                    elif hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
                        thumbnail = entry.media_thumbnail[0].get("url")

                    # Clean description
                    description_text = entry.get("summary", "")
                    if len(description_text) > 300:
                        description_text = description_text[:300] + "..."

                    article = {
                        "title": entry.title,
                        "url": entry.link,
                        "score": 0,  # RSS doesn't provide engagement metrics
                        "timestamp": timestamp,
                        "source": feed_name.upper(),
                        "source_type": "news",
                        "description": description_text,
                        "thumbnail": thumbnail,
                        "author": entry.get("author", feed_name),
                    }
                    articles.append(article)

                except Exception as e:
                    logger.warning(f"Failed to parse entry from {feed_name}: {e}")
                    continue

            logger.info(f"Found {len(articles)} relevant articles from {feed_name}")
            return articles

        except Exception as e:
            logger.error(f"Failed to fetch RSS feed from {feed_name}: {e}")
            return []

    def aggregate_for_game(self, keywords: List[str]) -> List[Dict]:
        """
        Aggregate news articles for a game from all configured RSS feeds.

        Args:
            keywords: List of keywords to filter for the game

        Returns:
            Combined list of articles from all news sources
        """
        all_articles = []

        for feed_name, feed_url in self.feeds.items():
            articles = self.fetch_feed(feed_name, feed_url, keywords)
            all_articles.extend(articles)

        logger.info(f"Aggregated {len(all_articles)} total news articles")
        return all_articles

    def is_official_source(self, article: Dict, official_sources: List[str]) -> bool:
        """
        Check if an article is from an official source.

        Args:
            article: Article dictionary
            official_sources: List of official source names

        Returns:
            True if article is from official source
        """
        title = article.get("title", "").lower()
        source = article.get("source", "").lower()
        description = article.get("description", "").lower()

        content = f"{title} {source} {description}"

        return any(official.lower() in content for official in official_sources)
