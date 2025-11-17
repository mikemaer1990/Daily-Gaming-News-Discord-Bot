"""Reddit content aggregator using web scraping and RSS feeds."""
import requests
import feedparser
import logging
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from typing import List, Dict, Optional

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    REDDIT_USER_AGENT, REDDIT_REQUEST_DELAY, REDDIT_TIMEOUT,
    MAX_CONTENT_AGE_DAYS
)

logger = logging.getLogger(__name__)


class RedditAggregator:
    """Aggregates content from Reddit subreddits."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": REDDIT_USER_AGENT})

    def get_subreddit_content(self, subreddit: str, limit: int = 25) -> List[Dict]:
        """
        Fetch content from a subreddit using RSS feed (primary) or web scraping (fallback).

        Args:
            subreddit: Name of the subreddit (without r/)
            limit: Maximum number of posts to fetch

        Returns:
            List of post dictionaries with title, url, score, timestamp, etc.
        """
        logger.info(f"Fetching content from r/{subreddit}")

        # Try RSS feed first (more reliable and respectful)
        posts = self._fetch_via_rss(subreddit, limit)

        if not posts:
            logger.warning(f"RSS feed failed for r/{subreddit}, trying web scraping")
            posts = self._fetch_via_scraping(subreddit, limit)

        # Filter out old content
        cutoff_date = datetime.utcnow() - timedelta(days=MAX_CONTENT_AGE_DAYS)
        filtered_posts = [
            post for post in posts
            if post.get("timestamp") and post["timestamp"] > cutoff_date
        ]

        logger.info(f"Retrieved {len(filtered_posts)} recent posts from r/{subreddit}")
        return filtered_posts

    def _fetch_via_rss(self, subreddit: str, limit: int) -> List[Dict]:
        """Fetch posts using Reddit RSS feed."""
        try:
            rss_url = f"https://www.reddit.com/r/{subreddit}/.rss?limit={limit}"
            feed = feedparser.parse(rss_url)

            posts = []
            for entry in feed.entries[:limit]:
                try:
                    # Parse timestamp
                    timestamp = datetime(*entry.published_parsed[:6])

                    # Extract score from content if available (not always present in RSS)
                    score = 0

                    post = {
                        "title": entry.title,
                        "url": entry.link,
                        "score": score,  # RSS doesn't provide score, will use 0
                        "timestamp": timestamp,
                        "source": f"r/{subreddit}",
                        "source_type": "reddit",
                        "author": entry.get("author", "unknown"),
                        "description": self._clean_description(entry.get("summary", "")),
                    }
                    posts.append(post)
                except Exception as e:
                    logger.warning(f"Failed to parse RSS entry: {e}")
                    continue

            return posts

        except Exception as e:
            logger.error(f"Failed to fetch RSS feed for r/{subreddit}: {e}")
            return []

    def _fetch_via_scraping(self, subreddit: str, limit: int) -> List[Dict]:
        """Fetch posts via web scraping (fallback method)."""
        try:
            url = f"https://old.reddit.com/r/{subreddit}/"
            response = self.session.get(url, timeout=REDDIT_TIMEOUT)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            posts = []

            # Find all post containers
            post_containers = soup.find_all("div", class_="thing", limit=limit)

            for container in post_containers:
                try:
                    # Extract post data
                    title_elem = container.find("a", class_="title")
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    url = title_elem.get("href", "")

                    # Make relative URLs absolute
                    if url.startswith("/r/"):
                        url = f"https://reddit.com{url}"

                    # Extract score
                    score_elem = container.find("div", class_="score")
                    score = 0
                    if score_elem:
                        score_text = score_elem.get("title", "0")
                        try:
                            score = int(score_text)
                        except ValueError:
                            score = 0

                    # Extract timestamp
                    time_elem = container.find("time")
                    timestamp = datetime.utcnow()
                    if time_elem and time_elem.get("datetime"):
                        try:
                            timestamp = datetime.fromisoformat(
                                time_elem["datetime"].replace("Z", "+00:00")
                            )
                        except Exception:
                            pass

                    # Extract author
                    author_elem = container.find("a", class_="author")
                    author = author_elem.get_text(strip=True) if author_elem else "unknown"

                    post = {
                        "title": title,
                        "url": url,
                        "score": score,
                        "timestamp": timestamp,
                        "source": f"r/{subreddit}",
                        "source_type": "reddit",
                        "author": author,
                        "description": title,  # Use title as description for scraped posts
                    }
                    posts.append(post)

                except Exception as e:
                    logger.warning(f"Failed to parse post container: {e}")
                    continue

            # Rate limiting
            time.sleep(REDDIT_REQUEST_DELAY)

            return posts

        except Exception as e:
            logger.error(f"Failed to scrape r/{subreddit}: {e}")
            return []

    def _clean_description(self, html_content: str) -> str:
        """Clean HTML content to plain text."""
        try:
            soup = BeautifulSoup(html_content, "lxml")
            text = soup.get_text(separator=" ", strip=True)
            # Limit length
            return text[:300] + "..." if len(text) > 300 else text
        except Exception:
            return ""

    def aggregate_for_game(self, subreddits: List[str]) -> List[Dict]:
        """
        Aggregate content from multiple subreddits for a game.

        Args:
            subreddits: List of subreddit names

        Returns:
            Combined list of posts from all subreddits
        """
        all_posts = []

        for subreddit in subreddits:
            posts = self.get_subreddit_content(subreddit)
            all_posts.extend(posts)

            # Be respectful with rate limiting
            if len(subreddits) > 1:
                time.sleep(REDDIT_REQUEST_DELAY)

        return all_posts
