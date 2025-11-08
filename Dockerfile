FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1         PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY bot /app/bot
COPY README.md /app/README.md

# Default: polling runner
CMD ["python", "-m", "bot.main"]

# For webhook mode, build with:
#   docker build -t tg-openrouter-bot:wh .
# and override CMD:
#   docker run --rm -p 8080:8080 --env-file .env tg-openrouter-bot:wh python -m bot.webhook
