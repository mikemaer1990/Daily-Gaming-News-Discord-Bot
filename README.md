# CS2 Weekly Digest Discord Bot

A Discord bot that sends a weekly curated digest of Counter-Strike 2 content — news, guides, pro scene updates, and community highlights from across the web.

## Features

- Weekly automated digest every Friday at 8 AM PST
- 15 items per digest with a mix of:
  - YouTube videos (~50%): news, guides, pro match highlights, tournament recaps
  - Reddit posts: r/GlobalOffensive, r/cs2
  - Articles: HLTV, Dot Esports, PC Gamer, Polygon, VG247, Eurogamer
- Also includes a general "Top Gaming News" section
- Smart content prioritization (official/patch notes > major news > community)
- Deduplication across sources
- Discord link previews suppressed for cleaner formatting

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

4. Add your credentials to `.env`:
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
3. Create a new webhook
4. Copy the webhook URL to your `.env` file

## Usage

### Local Testing

```bash
python src/main.py
```

### GitHub Actions Deployment

The bot runs automatically via GitHub Actions every Friday at 8 AM PST.

1. Add secrets to your repository (Settings > Secrets and variables > Actions):
   - `DISCORD_WEBHOOK_URL`
   - `YOUTUBE_API_KEY`

2. To trigger manually: Actions tab > "Weekly CS2 Digest" > Run workflow

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
│   │   ├── reddit_aggregator.py     # Reddit RSS
│   │   ├── youtube_aggregator.py    # YouTube Data API
│   │   └── news_aggregator.py       # RSS feed parsing
│   ├── processors/
│   │   ├── content_ranker.py        # Content prioritization
│   │   └── deduplicator.py          # Duplicate removal
│   └── discord/
│       └── webhook_sender.py         # Discord webhook
├── .env.example
├── requirements.txt
└── README.md
```

## Content Prioritization

1. **Official** — Valve announcements, patch notes
2. **Major News** — Coverage from HLTV, Dot Esports, established outlets; ESL/BLAST tournament content
3. **Community** — High-engagement Reddit posts, creator content
4. **Discussion** — Analysis, opinion pieces

## License

MIT License
