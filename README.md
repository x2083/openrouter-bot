# Telegram AI Assistant (Python + OpenRouter)

A minimal, production-ready Telegram bot that sends user messages to an AI model via [OpenRouter](https://openrouter.ai) and returns answers.
- Language: Python 3.11+
- Telegram framework: `python-telegram-bot` v21 (async)
- HTTP client: `httpx`
- Run mode: polling (simple), webhook-ready (optional)
- Container: Dockerfile provided + docker-compose example

## 1) Configure environment

Copy `.env.example` to `.env` and fill values:

```env
TELEGRAM_BOT_TOKEN=123456:ABC...
OPENROUTER_API_KEY=or-xxxxxxxxxxxxxxxxxxxxxxxxxx
OPENROUTER_MODEL=openai/gpt-4o-mini
SYSTEM_PROMPT=You are a helpful assistant. Keep answers concise.
OR_SITE_URL=https://example.com
OR_APP_NAME=Telegram AI Assistant
MAX_TOKENS=800
TEMPERATURE=0.3
```

Notes:
- `OR_SITE_URL` and `OR_APP_NAME` are optional but recommended by OpenRouter for attribution headers.
- `SYSTEM_PROMPT` sets the bot's default role/personality.
- Adjust `OPENROUTER_MODEL` to any model listed on OpenRouter (e.g., `anthropic/claude-3.5-sonnet`, `openai/gpt-4.1-mini`, etc.).

## 2) Run locally (Python)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export $(grep -v '^#' .env | xargs -d '\n')
python -m bot.main
```

## 3) Run with Docker

Build and run:

```bash
docker build -t tg-openrouter-bot:latest .
# using your local .env file
docker run --rm -it --env-file .env tg-openrouter-bot:latest
```

Or with docker-compose:

```bash
docker compose up --build
```

## 4) Webhook (optional)

This template defaults to polling for simplicity. If you must use webhooks (e.g., on some PaaS),
you can:
- Set `WEBHOOK_URL` in `.env` to your public HTTPS endpoint
- Expose port 8080
- Start `bot.webhook` instead (see comments in `Dockerfile`)

## 5) Project structure

```
.
├── bot
│   ├── __init__.py
│   ├── config.py
│   ├── main.py          # polling entrypoint
│   ├── webhook.py       # webhook entrypoint (optional)
│   └── openrouter_client.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## 6) Commands (Telegram)

- `/start` — greet and brief help
- `/help` — usage tips
- Any text message — forwarded to the AI model via OpenRouter

## 7) Security notes

- Never hardcode tokens; use environment variables.
- Rotate `OPENROUTER_API_KEY` and `TELEGRAM_BOT_TOKEN` if leaked.
- Consider rate limiting or user allowlists for public bots.

## 8) Troubleshooting

- **403 from OpenRouter**: check `OPENROUTER_API_KEY`; make sure headers include `Authorization` + optional `HTTP-Referer`/`X-Title`.
- **Bot not responding**: verify `TELEGRAM_BOT_TOKEN` and that the bot isn't blocked; check logs.
- **Unicode errors**: this template enforces UTF‑8 everywhere.

Happy hacking!
