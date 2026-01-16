"""Discord webhook integration for sending formatted news digests."""
import requests
import logging
from datetime import datetime
from typing import List, Dict
import time

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    DISCORD_WEBHOOK_URL, MAX_RETRIES, RETRY_DELAY
)

logger = logging.getLogger(__name__)


class WebhookSender:
    """Sends formatted news digests to Discord via webhook."""

    def __init__(self, webhook_url: str = DISCORD_WEBHOOK_URL):
        self.webhook_url = webhook_url

    def format_game_message(
        self, game_name: str, items: List[Dict], is_trending: bool = False
    ) -> str:
        """
        Format a game's content as a simple numbered list.

        Args:
            game_name: Name of the game or section
            items: List of content items
            is_trending: Whether this is the trending section

        Returns:
            Formatted message string (max 2000 chars for Discord limit)
        """
        MAX_MESSAGE_LENGTH = 2000
        MAX_TITLE_LENGTH = 100

        if not items:
            fallback_msg = "No trending news found this week." if is_trending else "No new content found this week."
            return f"**{game_name} - Top {len(items)}**\n\n{fallback_msg}"

        # Start with header
        message = f"**{game_name} - Top {len(items)}**\n\n"

        # Add each item as numbered list
        for idx, item in enumerate(items, 1):
            source = item.get("source", "Unknown")
            title = item.get("title", "No title").strip()
            url = item.get("url", "")

            # Truncate long titles
            if len(title) > MAX_TITLE_LENGTH:
                title = title[:MAX_TITLE_LENGTH - 3] + "..."

            # Format as: 1. [Source] Title - <URL>
            # Angle brackets prevent Discord from generating link previews
            line = f"{idx}. [{source}] {title} - <{url}>\n"

            # Check if adding this line would exceed the limit
            if len(message) + len(line) > MAX_MESSAGE_LENGTH:
                # Truncate and add indicator that items were cut
                remaining = MAX_MESSAGE_LENGTH - len(message) - 20
                if remaining > 0:
                    message += f"... and {len(items) - idx + 1} more items"
                break

            message += line

        return message

    def send_digest(self, game_digests: Dict[str, Dict]) -> bool:
        """
        Send the complete news digest to Discord.

        Args:
            game_digests: Dictionary mapping game IDs to their digest data
                         Each digest should have: name, items

        Returns:
            True if successful, False otherwise
        """
        try:
            # Send weekly digest header
            header = f"# Weekly Gaming News Digest - {datetime.utcnow().strftime('%B %d, %Y')}\n"
            payload = {"content": header}

            try:
                response = requests.post(self.webhook_url, json=payload, timeout=30)
                response.raise_for_status()
                logger.info("Sent weekly digest header")
            except Exception as e:
                logger.warning(f"Failed to send header: {e}")

            time.sleep(1)

            # Define section order: trending first, then games
            section_order = []
            if "trending" in game_digests:
                section_order.append("trending")

            # Add all other game sections
            for game_id in game_digests.keys():
                if game_id != "trending":
                    section_order.append(game_id)

            # Send one message per section
            for game_id in section_order:
                digest = game_digests[game_id]
                game_name = digest["name"]
                items = digest.get("items", [])

                # Check if this is the trending section
                is_trending = (game_id == "trending")

                # Format message
                message_content = self.format_game_message(game_name, items, is_trending)

                # Prepare payload as simple text message
                payload = {"content": message_content}

                # Send with retry logic
                for attempt in range(1, MAX_RETRIES + 1):
                    try:
                        response = requests.post(
                            self.webhook_url,
                            json=payload,
                            timeout=30
                        )
                        response.raise_for_status()

                        logger.info(f"Successfully sent {game_name} digest to Discord")
                        break

                    except requests.exceptions.RequestException as e:
                        logger.error(f"Attempt {attempt}/{MAX_RETRIES} failed for {game_name}: {e}")

                        if attempt < MAX_RETRIES:
                            logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                            time.sleep(RETRY_DELAY)
                        else:
                            logger.error(f"All retry attempts failed for {game_name}")
                            return False

                # Small delay between messages to avoid rate limiting
                time.sleep(1)

            logger.info("Successfully sent all sections to Discord")
            return True

        except Exception as e:
            logger.error(f"Failed to send digest: {e}")
            return False

    def send_error_notification(self, error_message: str) -> bool:
        """
        Send an error notification to Discord.

        Args:
            error_message: Error message to send

        Returns:
            True if successful, False otherwise
        """
        try:
            embed = {
                "title": "⚠️ Gaming News Bot Error",
                "description": f"An error occurred while generating the news digest:\n\n{error_message}",
                "color": 15158332,  # Red
                "timestamp": datetime.utcnow().isoformat()
            }

            payload = {"embeds": [embed]}

            response = requests.post(self.webhook_url, json=payload, timeout=30)
            response.raise_for_status()

            logger.info("Sent error notification to Discord")
            return True

        except Exception as e:
            logger.error(f"Failed to send error notification: {e}")
            return False
