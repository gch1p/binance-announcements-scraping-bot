# binance-announcements-scraping-bot

Fork of https://github.com/darroyolpz/Binance-Announcements.

- Fixed html markup parsing
- Removed discord
- Added Telegram notifications

## Usage

Crontab example, runs every four hours:

```
MY_TELEGRAM_CHAT_ID=
MY_TELEGRAM_TOKEN=""
MY_STATE_FILE="$HOME/.binance-scraping-state"

0 */4 * * * /path/to/binance-announcements-scraping-bot/binance-announcements-scraping-bot.py
```

## License

MIT