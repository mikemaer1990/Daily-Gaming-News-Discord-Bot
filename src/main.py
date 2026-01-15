"""Main entry point for the gaming news bot."""
import logging
import sys
import io
from typing import Dict, List

from config import GAMES, LOG_LEVEL, LOG_FORMAT, ITEMS_PER_GAME
from aggregators.reddit_aggregator import RedditAggregator
from aggregators.youtube_aggregator import YouTubeAggregator
from aggregators.news_aggregator import NewsAggregator
from processors.content_ranker import ContentRanker
from processors.deduplicator import Deduplicator
from discord.webhook_sender import WebhookSender

# Setup logging with UTF-8 encoding for Windows compatibility
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'))
    ]
)
logger = logging.getLogger(__name__)


def aggregate_content_for_game(
    game_id: str, game_config: Dict
) -> List[Dict]:
    """
    Aggregate content from all sources for a specific game.

    Args:
        game_id: Game identifier
        game_config: Game configuration dictionary

    Returns:
        List of all aggregated content items
    """
    logger.info(f"Aggregating content for {game_config['name']}")

    all_content = []

    # Initialize aggregators
    reddit_agg = RedditAggregator()
    youtube_agg = YouTubeAggregator()
    news_agg = NewsAggregator()

    # Aggregate from Reddit
    try:
        logger.info("Fetching from Reddit...")
        reddit_posts = reddit_agg.aggregate_for_game(game_config["subreddits"])
        all_content.extend(reddit_posts)
        logger.info(f"Got {len(reddit_posts)} Reddit posts")
    except Exception as e:
        logger.error(f"Failed to aggregate Reddit content: {e}")

    # Aggregate from YouTube
    try:
        logger.info("Fetching from YouTube...")
        youtube_videos = youtube_agg.aggregate_for_game(game_config["keywords"])
        all_content.extend(youtube_videos)
        logger.info(f"Got {len(youtube_videos)} YouTube videos")
    except Exception as e:
        logger.error(f"Failed to aggregate YouTube content: {e}")

    # Aggregate from news sites
    try:
        logger.info("Fetching from news sites...")
        news_articles = news_agg.aggregate_for_game(game_config["keywords"])
        all_content.extend(news_articles)
        logger.info(f"Got {len(news_articles)} news articles")
    except Exception as e:
        logger.error(f"Failed to aggregate news content: {e}")

    logger.info(f"Total content items for {game_config['name']}: {len(all_content)}")
    return all_content


def process_and_rank_content(
    content: List[Dict], game_config: Dict
) -> List[Dict]:
    """
    Process, deduplicate, and rank content.

    Args:
        content: List of content items
        game_config: Game configuration dictionary

    Returns:
        Top ranked and deduplicated items
    """
    if not content:
        logger.warning(f"No content to process for {game_config['name']}")
        return []

    # Initialize processors
    deduplicator = Deduplicator()
    ranker = ContentRanker()

    # Deduplicate first
    unique_content = deduplicator.deduplicate(content)
    logger.info(f"After deduplication: {len(unique_content)} items")

    # Rank and select top items
    top_items = ranker.select_top_items(
        unique_content,
        game_config["official_sources"],
        count=ITEMS_PER_GAME
    )
    logger.info(f"Selected top {len(top_items)} items")

    return top_items


def main():
    """Main execution function."""
    logger.info("=" * 60)
    logger.info("Gaming News Bot - Starting Weekly Digest Generation")
    logger.info("=" * 60)

    try:
        # Prepare digests for all games
        game_digests = {}

        for game_id, game_config in GAMES.items():
            logger.info(f"\n{'=' * 60}")
            logger.info(f"Processing {game_config['name']}")
            logger.info(f"{'=' * 60}")

            # Aggregate content
            content = aggregate_content_for_game(game_id, game_config)

            # Process and rank
            top_items = process_and_rank_content(content, game_config)

            # Store digest
            game_digests[game_id] = {
                "name": game_config["name"],
                "items": top_items
            }

        # Aggregate trending gaming news (general, not game-specific)
        logger.info(f"\n{'=' * 60}")
        logger.info("Aggregating Trending Gaming News")
        logger.info(f"{'=' * 60}")

        trending_items = []
        try:
            news_agg = NewsAggregator()
            trending_items = news_agg.aggregate_trending_gaming_news(count=3)
            logger.info(f"Got {len(trending_items)} trending gaming news items")
        except Exception as e:
            logger.error(f"Failed to aggregate trending gaming news: {e}")

        # Add trending section to digests
        game_digests["trending"] = {
            "name": "Top Gaming News",
            "items": trending_items
        }

        # Send to Discord
        logger.info(f"\n{'=' * 60}")
        logger.info("Sending digest to Discord")
        logger.info(f"{'=' * 60}")

        webhook_sender = WebhookSender()
        success = webhook_sender.send_digest(game_digests)

        if success:
            logger.info("✓ Successfully sent weekly gaming news digest!")
            return 0
        else:
            logger.error("✗ Failed to send digest to Discord")
            return 1

    except Exception as e:
        logger.error(f"Critical error in main execution: {e}", exc_info=True)

        # Try to send error notification
        try:
            webhook_sender = WebhookSender()
            webhook_sender.send_error_notification(str(e))
        except Exception:
            pass

        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
