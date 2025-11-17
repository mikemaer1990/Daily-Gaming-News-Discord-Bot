# Gaming News Discord Bot

A Discord bot that sends daily curated news digests for Battlefield 6 and Arc Raiders, combining official news, community clips, and stories from multiple sources.

## Features

- Daily automated news digest at 2:00 PM PST
- Curates top 5 items per game (Battlefield 6 and Arc Raiders)
- Aggregates content from multiple sources:
  - Reddit (r/battlefield, r/Battlefield6, r/arcraiders)
  - YouTube (via YouTube Data API)
  - Gaming news sites (IGN, Kotaku, PC Gamer, Polygon, VG247, Eurogamer) via RSS
- Smart content prioritization (official news > major news > community highlights)
- Rich Discord embeds with thumbnails and formatted content
- Automatic timezone handling (PST/PDT with DST awareness)

## Setup

### Prerequisites

- Python 3.10 or higher
- YouTube Data API key
- Discord webhook URL

### Installation

1. Clone the repository:
```bash
git clone https://github.com/mikemaer1990/Daily-Gaming-News-Discord-Bot.git
cd Daily-Gaming-News-Discord-Bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

4. Edit `.env` and add your credentials:
```env
DISCORD_WEBHOOK_URL=your_webhook_url_here
YOUTUBE_API_KEY=your_youtube_api_key_here
```

### Getting API Keys

#### YouTube Data API v3:
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable YouTube Data API v3
4. Create credentials (API key)
5. Copy the API key to your `.env` file

#### Discord Webhook:
1. Go to your Discord server settings
2. Navigate to Integrations > Webhooks
3. Create a new webhook or use existing one
4. Copy the webhook URL to your `.env` file

## Usage

### Local Testing

Run the bot manually:
```bash
python src/main.py
```

### GitHub Actions Deployment

The bot runs automatically via GitHub Actions at 2:00 PM PST daily.

1. Configure GitHub Secrets:
   - Go to your repository Settings > Secrets and variables > Actions
   - Add the following secrets:
     - `DISCORD_WEBHOOK_URL`
     - `YOUTUBE_API_KEY`

2. The workflow will run automatically based on the schedule
3. You can also trigger it manually:
   - Go to Actions tab
   - Select "Daily Gaming News Digest"
   - Click "Run workflow"

## Project Structure

```
gaming-news-bot/
├── .github/
│   └── workflows/
│       └── daily-gaming-news.yml    # GitHub Actions workflow
├── src/
│   ├── main.py                      # Entry point
│   ├── config.py                    # Configuration and constants
│   ├── aggregators/
│   │   ├── __init__.py
│   │   ├── reddit_aggregator.py    # Reddit scraping
│   │   ├── youtube_aggregator.py   # YouTube API integration
│   │   └── news_aggregator.py      # RSS feed parsing
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── content_ranker.py       # Content prioritization
│   │   └── deduplicator.py         # Duplicate removal
│   └── discord/
│       ├── __init__.py
│       └── webhook_sender.py        # Discord embed creation
├── .env.example                     # Example environment variables
├── .gitignore
├── requirements.txt
└── README.md
```

## Content Prioritization

The bot uses a multi-tier priority system:

1. **Official News** - Announcements, patches, updates from developers
2. **Major News** - Reviews, previews, interviews from established outlets
3. **Community Highlights** - Viral clips, community discoveries
4. **General Discussion** - Opinion pieces, analysis

Content is selected based on:
- Recency (last 24-48 hours preferred)
- Engagement metrics (upvotes, views, likes)
- Source credibility
- Content diversity

## Error Handling

- Graceful fallbacks if sources are unavailable
- Retry logic for API failures
- Comprehensive logging for debugging
- Continues with available sources if some fail

## License

MIT License - see LICENSE file for details

## Contributing

Feel free to open issues or submit pull requests for improvements!
