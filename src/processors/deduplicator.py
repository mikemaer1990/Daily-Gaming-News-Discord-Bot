"""Content deduplication to avoid showing the same story multiple times."""
import logging
from typing import List, Dict
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class Deduplicator:
    """Removes duplicate content items based on URL and title similarity."""

    def __init__(self, similarity_threshold: float = 0.85):
        """
        Initialize deduplicator.

        Args:
            similarity_threshold: Title similarity threshold (0-1) for considering items duplicates
        """
        self.similarity_threshold = similarity_threshold

    def are_titles_similar(self, title1: str, title2: str) -> bool:
        """
        Check if two titles are similar enough to be considered duplicates.

        Args:
            title1: First title
            title2: Second title

        Returns:
            True if titles are similar
        """
        # Normalize titles
        t1 = title1.lower().strip()
        t2 = title2.lower().strip()

        # Exact match
        if t1 == t2:
            return True

        # Use SequenceMatcher for fuzzy matching
        similarity = SequenceMatcher(None, t1, t2).ratio()
        return similarity >= self.similarity_threshold

    def deduplicate(self, items: List[Dict]) -> List[Dict]:
        """
        Remove duplicate items from the list.

        Deduplication strategy:
        1. Remove exact URL duplicates (keep first occurrence)
        2. Remove items with highly similar titles (keep higher ranked)

        Args:
            items: List of content items (should be pre-sorted by rank)

        Returns:
            Deduplicated list of items
        """
        if not items:
            return []

        unique_items = []
        seen_urls = set()
        seen_titles = []

        for item in items:
            url = item.get("url", "")
            title = item.get("title", "")

            # Skip if URL already seen
            if url and url in seen_urls:
                logger.debug(f"Skipping duplicate URL: {title[:50]}")
                continue

            # Check for similar titles
            is_duplicate = False
            for seen_title in seen_titles:
                if self.are_titles_similar(title, seen_title):
                    logger.debug(
                        f"Skipping similar title: '{title[:50]}' "
                        f"(similar to '{seen_title[:50]}')"
                    )
                    is_duplicate = True
                    break

            if is_duplicate:
                continue

            # Add to unique items
            unique_items.append(item)
            if url:
                seen_urls.add(url)
            seen_titles.append(title)

        logger.info(
            f"Deduplication: {len(items)} items -> {len(unique_items)} unique items "
            f"({len(items) - len(unique_items)} duplicates removed)"
        )

        return unique_items

    def deduplicate_across_games(
        self, game_items: Dict[str, List[Dict]]
    ) -> Dict[str, List[Dict]]:
        """
        Deduplicate items across multiple games (e.g., general gaming news).

        Args:
            game_items: Dictionary mapping game IDs to their content items

        Returns:
            Dictionary with deduplicated items per game
        """
        # Deduplicate within each game first
        deduplicated = {}

        for game_id, items in game_items.items():
            deduplicated[game_id] = self.deduplicate(items)

        # Cross-game deduplication (optional - for now, just return within-game dedup)
        # Could be extended to check if same article appears in multiple game feeds

        return deduplicated
