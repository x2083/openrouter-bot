import asyncio
import logging
import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from telegram import Update
from .config import load_settings
from .openrouter_client import OpenRouterClient
from aiohttp import web

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s | %(message)s")

settings = load_settings()
if not settings.telegram_token or not settings.openrouter_api_key:
    raise SystemExit("Missing TELEGRAM_BOT_TOKEN or OPENROUTER_API_KEY env vars.")

or_client = OpenRouterClient(
    api_key=settings.openrouter_api_key,
    site_url=settings.or_site_url,
    app_name=settings.or_app_name,
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я работаю в режиме webhook. Отправь вопрос текстом.")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправь текст — я спрошу модель через OpenRouter и верну ответ.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = (update.message.text or "").strip()
    if not user_text:
        await update.message.reply_text("Отправь обычный текстовый вопрос.")
        return
    try:
        reply = await or_client.chat(
            model=settings.openrouter_model,
            user_text=user_text,
            system_prompt=settings.system_prompt,
            max_tokens=settings.max_tokens,
            temperature=settings.temperature,
        )
        await update.message.reply_text(reply)
    except Exception:
        await update.message.reply_text("Ошибка обращения к OpenRouter. Проверь ключ и модель.")

async def main():
    application = ApplicationBuilder().token(settings.telegram_token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await application.initialize()

    if not settings.webhook_url:
        raise SystemExit("WEBHOOK_URL is not set; cannot start webhook mode.")

    # Bind Telegram webhook to aiohttp app
    async def on_startup(app):
        await application.bot.set_webhook(url=settings.webhook_url)

    async def on_cleanup(app):
        await application.bot.delete_webhook()

    app = web.Application()
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    app.router.add_post("/", application.webhook_handler())

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()

    logging.info("Webhook app listening on 0.0.0.0:8080")
    # Keep running
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        import uvloop
        uvloop.install()
    except Exception:
        pass
    asyncio.run(main())
