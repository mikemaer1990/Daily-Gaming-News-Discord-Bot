"""Content ranking and prioritization logic."""
import logging
from datetime import datetime, timedelta
from typing import List, Dict

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    PRIORITY_WEIGHTS, PREFERRED_CONTENT_AGE_HOURS,
    FALLBACK_CONTENT_AGE_HOURS, ITEMS_PER_GAME, SOURCE_DISTRIBUTION
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
        Select the top N items ensuring diversity of source types with balanced distribution.

        Args:
            items: List of content items
            official_sources: List of official source names
            count: Number of items to select

        Returns:
            Top N items with balanced source diversity
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

        # Calculate target distribution based on SOURCE_DISTRIBUTION config
        # Target the midpoint of each range
        target_distribution = {}
        for source_type, (min_val, max_val) in SOURCE_DISTRIBUTION.items():
            target_distribution[source_type] = (min_val + max_val) // 2

        selected = []
        selected_ids = set()  # Track selected item IDs to avoid duplicates

        # First pass: Try to get target number from each source
        remaining_slots = count
        for source_type in ["news", "reddit", "youtube"]:  # Order by priority
            target = target_distribution.get(source_type, 0)
            available = by_source[source_type]

            # Adjust target if we don't have enough slots remaining
            actual_target = min(target, remaining_slots, len(available))

            # Select top-ranked items from this source
            for item in available[:actual_target]:
                item_id = item.get("url", id(item))
                if item_id not in selected_ids:
                    selected.append(item)
                    selected_ids.add(item_id)
                    remaining_slots -= 1

        # Second pass: Fill remaining slots with highest-ranked items from any source
        if remaining_slots > 0:
            for item in ranked_items:
                item_id = item.get("url", id(item))
                if item_id not in selected_ids:
                    selected.append(item)
                    selected_ids.add(item_id)
                    remaining_slots -= 1
                    if remaining_slots <= 0:
                        break

        # Sort selected items by rank score to maintain quality ordering
        selected.sort(key=lambda x: x["rank_score"], reverse=True)

        # Trim to exact count if we went over
        selected = selected[:count]

        # Count by source for logging
        source_counts = {"reddit": 0, "youtube": 0, "news": 0}
        for item in selected:
            source_type = item.get("source_type", "")
            if source_type in source_counts:
                source_counts[source_type] += 1

        logger.info(
            f"Selected {len(selected)} items with source distribution: {source_counts} "
            f"(target: {target_distribution})"
        )

        return selected
