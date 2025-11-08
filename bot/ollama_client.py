import httpx

class OllamaClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def chat(self, model: str, user_text: str, system_prompt: str,
                   max_tokens: int = 800, temperature: float = 0.3) -> str:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            "options": {
                "temperature": temperature,
                # Ограничим длину ответа, чтобы ускорить:
                "num_predict": max(1, min(max_tokens, 4096)),
            },
            "stream": False
        }
        url = f"{self.base_url}/api/chat"
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(url, json=payload)
            r.raise_for_status()
            data = r.json()
            if isinstance(data, dict) and "message" in data and isinstance(data["message"], dict):
                content = data["message"].get("content")
                if isinstance(content, str):
                    return content.strip()
            # fallback
            return str(data)
