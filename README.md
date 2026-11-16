# Cashy

Telegram currency converter bot — [@cashyfy_bot](https://t.me/cashyfy_bot).

## Commands

- `/start` — welcome message
- `100 USD to INR` — convert an amount (just send it as a message)
- `/convert 100 USD INR` — same thing
- `/rates` — popular rates vs INR
- `/help` — help

## Run it

```bash
export TELEGRAM_BOT_TOKEN="your-bot-token"
python3 bot.py
```

Rates come from the free exchangerate-api (no key needed) and are cached for 1 hour.

## Security

Never commit your bot token. It is read from the `TELEGRAM_BOT_TOKEN` environment variable only. If a token was ever shared in chat, rotate it with @BotFather (`/revoke`) and set the new one.
