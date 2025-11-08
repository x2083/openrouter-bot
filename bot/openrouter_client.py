# bot/openrouter_client.py
import httpx
from typing import Optional

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

class OpenRouterClient:
    def __init__(self, api_key: str, site_url: Optional[str]=None, app_name: Optional[str]=None):
        self.api_key = api_key
        self.site_url = site_url
        self.app_name = app_name

    async def chat(self, model: str, user_text: str, system_prompt: str,
                   max_tokens: int = 800, temperature: float = 0.3) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.site_url:
            headers["HTTP-Referer"] = self.site_url
        if self.app_name:
            headers["X-Title"] = self.app_name

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        async with httpx.AsyncClient(timeout=60) as client:
            try:
                r = await client.post(OPENROUTER_URL, headers=headers, json=payload)
                r.raise_for_status()
            except httpx.HTTPStatusError as e:
                code = e.response.status_code
                body = e.response.text
                if code == 402:
                    # вернём дружелюбный текст для пользователя
                    raise RuntimeError("Недостаточно кредитов в OpenRouter (HTTP 402). Пополните баланс или замените ключ.") from e
                raise RuntimeError(f"OpenRouter HTTP {code}: {body}") from e
            except Exception as e:
                raise RuntimeError(f"OpenRouter request failed: {e}") from e

            data = r.json()
            return data["choices"][0]["message"]["content"].strip()
