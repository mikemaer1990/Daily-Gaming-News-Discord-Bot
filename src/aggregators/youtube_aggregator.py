"""YouTube content aggregator using YouTube Data API v3."""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    YOUTUBE_API_KEY, YOUTUBE_MAX_RESULTS, YOUTUBE_SEARCH_DAYS,
    MAX_CONTENT_AGE_DAYS
)

logger = logging.getLogger(__name__)


class YouTubeAggregator:
    """Aggregates video content from YouTube."""

    def __init__(self):
        try:
            self.youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        except Exception as e:
            logger.error(f"Failed to initialize YouTube API client: {e}")
            self.youtube = None

    def search_videos(self, query: str, max_results: int = YOUTUBE_MAX_RESULTS) -> List[Dict]:
        """
        Search for YouTube videos related to a query.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of video dictionaries with title, url, views, timestamp, etc.
        """
        if not self.youtube:
            logger.error("YouTube API client not initialized")
            return []

        try:
            # Calculate date range
            published_after = (
                datetime.utcnow() - timedelta(days=YOUTUBE_SEARCH_DAYS)
            ).isoformat("T") + "Z"

            # Search for videos
            search_response = self.youtube.search().list(
                q=query,
                part="id,snippet",
                type="video",
                maxResults=max_results,
                order="relevance",
                publishedAfter=published_after,
                relevanceLanguage="en",
                safeSearch="moderate"
            ).execute()

            videos = []
            video_ids = []

            # Extract video IDs
            for item in search_response.get("items", []):
                video_id = item["id"]["videoId"]
                video_ids.append(video_id)

            # Get video statistics
            if video_ids:
                stats_response = self.youtube.videos().list(
                    part="statistics,snippet,contentDetails",
                    id=",".join(video_ids)
                ).execute()

                for item in stats_response.get("items", []):
                    video = self._parse_video_item(item)
                    if video:
                        videos.append(video)

            logger.info(f"Found {len(videos)} YouTube videos for query: {query}")
            return videos

        except HttpError as e:
            logger.error(f"YouTube API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to search YouTube videos: {e}")
            return []

    def _parse_video_item(self, item: Dict) -> Optional[Dict]:
        """Parse a YouTube video item into our standard format."""
        try:
            video_id = item["id"]
            snippet = item["snippet"]
            statistics = item.get("statistics", {})

            # Parse timestamp
            published_at = snippet["publishedAt"]
            timestamp = datetime.fromisoformat(published_at.replace("Z", "+00:00"))

            # Check age
            cutoff_date = datetime.utcnow().replace(tzinfo=timestamp.tzinfo) - timedelta(
                days=MAX_CONTENT_AGE_DAYS
            )
            if timestamp < cutoff_date:
                return None

            # Extract view count (use as engagement metric)
            view_count = int(statistics.get("viewCount", 0))

            # Get thumbnail
            thumbnails = snippet.get("thumbnails", {})
            thumbnail_url = None
            if "high" in thumbnails:
                thumbnail_url = thumbnails["high"]["url"]
            elif "medium" in thumbnails:
                thumbnail_url = thumbnails["medium"]["url"]
            elif "default" in thumbnails:
                thumbnail_url = thumbnails["default"]["url"]

            video = {
                "title": snippet["title"],
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "score": view_count,  # Use views as score for ranking
                "timestamp": timestamp.replace(tzinfo=None),  # Remove timezone for consistency
                "source": snippet["channelTitle"],
                "source_type": "youtube",
                "description": snippet.get("description", "")[:300],
                "thumbnail": thumbnail_url,
                "author": snippet["channelTitle"],
            }

            return video

        except Exception as e:
            logger.warning(f"Failed to parse video item: {e}")
            return None

    def aggregate_for_game(self, keywords: List[str]) -> List[Dict]:
        """
        Aggregate YouTube videos for a game using multiple keywords.

        Args:
            keywords: List of search keywords

        Returns:
            Combined list of videos from all keyword searches
        """
        all_videos = []
        seen_ids = set()

        for keyword in keywords:
            videos = self.search_videos(keyword, max_results=5)

            # Deduplicate by URL
            for video in videos:
                if video["url"] not in seen_ids:
                    all_videos.append(video)
                    seen_ids.add(video["url"])

        logger.info(f"Aggregated {len(all_videos)} unique YouTube videos")
        return all_videos
