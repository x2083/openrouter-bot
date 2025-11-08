import logging
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from .config import load_settings
from .openrouter_client import OpenRouterClient
from .ollama_client import OllamaClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")

settings = load_settings()
if not settings.telegram_token:
    raise SystemExit("Missing TELEGRAM_BOT_TOKEN env var.")

# Выбираем провайдера LLM
if settings.llm_provider.lower() == "ollama":
    llm_client = OllamaClient(settings.ollama_base_url)
    current_model = settings.ollama_model
    logging.info("LLM provider: Ollama (%s)", current_model)
else:
    if not settings.openrouter_api_key:
        raise SystemExit("Missing OPENROUTER_API_KEY for OpenRouter provider.")
    llm_client = OpenRouterClient(
        api_key=settings.openrouter_api_key,
        site_url=settings.or_site_url,
        app_name=settings.or_app_name,
    )
    current_model = settings.openrouter_model
    logging.info("LLM provider: OpenRouter (%s)", current_model)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я ИИ-бот. Напиши вопрос — отвечу.")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправь текст — я спрошу модель и верну ответ.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = (update.message.text or "").strip()
    if not user_text:
        return await update.message.reply_text("Отправь обычный текстовый вопрос.")
    # «печатает…»
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    try:
        reply = await llm_client.chat(
            model=current_model,
            user_text=user_text,
            system_prompt=settings.system_prompt,
            max_tokens=settings.max_tokens,
            temperature=settings.temperature,
        )
        await update.message.reply_text(reply)
    except Exception as e:
        logging.exception("LLM request failed")
        await update.message.reply_text(f"Ошибка запроса к модели: {e}")

def main():
    app = Application.builder().token(settings.telegram_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
