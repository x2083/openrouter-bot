from pydantic import BaseModel
import os

class Settings(BaseModel):
    telegram_token: str

    # Выбор провайдера: "openrouter" (платный API) или "ollama" (бесплатно, локально)
    llm_provider: str = "openrouter"

    # OpenRouter
    openrouter_api_key: str = ""
    openrouter_model: str = "openai/gpt-4o-mini"
    or_site_url: str | None = None
    or_app_name: str | None = None

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b-instruct"

    # Общие настройки генерации
    system_prompt: str = "Ты — дружелюбный и лаконичный ассистент. Отвечай на русском. Пиши кратко и по делу."
    max_tokens: int = 800
    temperature: float = 0.3
    webhook_url: str | None = None

def load_settings() -> Settings:
    return Settings(
        telegram_token=os.getenv("TELEGRAM_BOT_TOKEN", "").strip(),

        llm_provider=os.getenv("LLM_PROVIDER", "openrouter").strip(),

        # OpenRouter
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY", "").strip(),
        openrouter_model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini").strip(),
        or_site_url=(os.getenv("OR_SITE_URL") or None),
        or_app_name=(os.getenv("OR_APP_NAME") or None),

        # Ollama
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").strip(),
        ollama_model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct").strip(),

        # Общие
        system_prompt=os.getenv("SYSTEM_PROMPT", "Ты — дружелюбный и лаконичный ассистент. Отвечай на русском. Пиши кратко и по делу.").strip(),
        max_tokens=int(os.getenv("MAX_TOKENS", "800")),
        temperature=float(os.getenv("TEMPERATURE", "0.3")),
        webhook_url=(os.getenv("WEBHOOK_URL") or None),
    )
