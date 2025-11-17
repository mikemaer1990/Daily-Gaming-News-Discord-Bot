"""Content ranking and prioritization logic."""
import logging
from datetime import datetime, timedelta
from typing import List, Dict

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    PRIORITY_WEIGHTS, PREFERRED_CONTENT_AGE_HOURS,
    FALLBACK_CONTENT_AGE_HOURS, ITEMS_PER_GAME
)

logger = logging.getLogger(__name__)


class ContentRanker:
    """Ranks and selects the best content items based on priority and engagement."""

    def __init__(self):
        self.weights = PRIORITY_WEIGHTS

    def determine_content_type(self, item: Dict, official_sources: List[str]) -> str:
        """
        Determine the content type/priority level of an item.

        Args:
            item: Content item dictionary
            official_sources: List of official source names for the game

        Returns:
            Content type: 'official', 'major_news', 'community', or 'discussion'
        """
        title = item.get("title", "").lower()
        source = item.get("source", "").lower()
        source_type = item.get("source_type", "")
        description = item.get("description", "").lower()

        content = f"{title} {source} {description}"

        # Check for official sources
        if any(official.lower() in content for official in official_sources):
            return "official"

        # Check for official keywords in title
        official_keywords = [
            "patch", "update", "announcement", "release", "launch",
            "developer", "official", "confirmed"
        ]
        if any(keyword in title for keyword in official_keywords):
            return "official"

        # News articles from major outlets
        if source_type == "news":
            major_outlets = ["ign", "kotaku", "pc gamer", "polygon", "eurogamer", "vg247"]
            if any(outlet in source for outlet in major_outlets):
                return "major_news"

        # YouTube videos
        if source_type == "youtube":
            # Check if from official channels or major outlets
            trusted_channels = ["ign", "gamespot", "eurogamer", "pc gamer", "polygon"]
            if any(channel in source for channel in trusted_channels):
                return "major_news"
            else:
                return "community"

        # Reddit posts
        if source_type == "reddit":
            # High engagement community content
            if item.get("score", 0) > 500:
                return "community"
            else:
                return "discussion"

        # Default to discussion
        return "discussion"

    def calculate_score(self, item: Dict, content_type: str) -> float:
        """
        Calculate a ranking score for a content item.

        Args:
            item: Content item dictionary
            content_type: The content type/priority level

        Returns:
            Numerical score for ranking
        """
        # Base score from priority weight
        base_score = self.weights.get(content_type, 0)

        # Engagement boost (normalize score/views)
        engagement = item.get("score", 0)
        engagement_boost = 0

        if item.get("source_type") == "youtube":
            # YouTube views are much higher, normalize
            engagement_boost = min(engagement / 10000, 20)  # Cap at 20 points
        elif item.get("source_type") == "reddit":
            # Reddit upvotes
            engagement_boost = min(engagement / 100, 20)  # Cap at 20 points

        # Recency boost
        recency_boost = 0
        if item.get("timestamp"):
            hours_old = (datetime.utcnow() - item["timestamp"]).total_seconds() / 3600

            if hours_old <= PREFERRED_CONTENT_AGE_HOURS:
                # Very recent content gets a boost
                recency_boost = 25
            elif hours_old <= FALLBACK_CONTENT_AGE_HOURS:
                # Somewhat recent content gets a smaller boost
                recency_boost = 10

        total_score = base_score + engagement_boost + recency_boost

        logger.debug(
            f"Score breakdown for '{item.get('title', '')[:50]}': "
            f"base={base_score}, engagement={engagement_boost:.1f}, "
            f"recency={recency_boost}, total={total_score:.1f}"
        )

        return total_score

    def rank_content(
        self, items: List[Dict], official_sources: List[str]
    ) -> List[Dict]:
        """
        Rank content items by calculated scores.

        Args:
            items: List of content items
            official_sources: List of official source names

        Returns:
            Sorted list of items with added 'content_type' and 'rank_score' fields
        """
        ranked_items = []

        for item in items:
            content_type = self.determine_content_type(item, official_sources)
            score = self.calculate_score(item, content_type)

            item["content_type"] = content_type
            item["rank_score"] = score

            ranked_items.append(item)

        # Sort by score (highest first)
        ranked_items.sort(key=lambda x: x["rank_score"], reverse=True)

        logger.info(f"Ranked {len(ranked_items)} content items")
        return ranked_items

    def select_top_items(
        self, items: List[Dict], official_sources: List[str], count: int = ITEMS_PER_GAME
    ) -> List[Dict]:
        """
        Select the top N items ensuring diversity of source types.

        Args:
            items: List of content items
            official_sources: List of official source names
            count: Number of items to select

        Returns:
            Top N items with source diversity
        """
        # First rank all items
        ranked_items = self.rank_content(items, official_sources)

        if not ranked_items:
            logger.warning("No items to select from")
            return []

        # Group items by source type
        by_source = {
            "reddit": [],
            "youtube": [],
            "news": []
        }

        for item in ranked_items:
            source_type = item.get("source_type", "")
            if source_type in by_source:
                by_source[source_type].append(item)

        # Calculate how many items to pick from each source
        # Aim for roughly equal distribution, prioritizing sources with content
        available_sources = {k: v for k, v in by_source.items() if v}
        num_sources = len(available_sources)

        if num_sources == 0:
            logger.warning("No items available from any source")
            return []

        # Distribute items across sources
        selected = []
        items_per_source = max(1, count // num_sources)

        # Round-robin selection from each source
        for source_type in ["reddit", "youtube", "news"]:
            if source_type in available_sources:
                # Take top ranked items from this source
                source_items = by_source[source_type][:items_per_source]
                selected.extend(source_items)

        # If we don't have enough items yet, fill with highest-ranked remaining items
        if len(selected) < count:
            for item in ranked_items:
                if item not in selected:
                    selected.append(item)
                    if len(selected) >= count:
                        break

        # Trim to exact count if we went over
        selected = selected[:count]

        # Count by source for logging
        source_counts = {"reddit": 0, "youtube": 0, "news": 0}
        for item in selected:
            source_type = item.get("source_type", "")
            if source_type in source_counts:
                source_counts[source_type] += 1

        logger.info(
            f"Selected {len(selected)} items with source distribution: {source_counts}"
        )

        return selected
