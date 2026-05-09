import json
import logging
import httpx
from openai import AsyncOpenAI
from config import Config

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=Config().OPENAI_API_KEY, http_client=httpx.AsyncClient())
LANGS = ["ru", "uz", "en", "tr"]


async def translate_comment(text: str, source_lang: str = "ru") -> dict[str, str]:
    if not text or not text.strip():
        return {l: "" for l in LANGS}
    prompt = f"""Translate this construction site comment VERBATIM to Russian, Uzbek, English, Turkish.
Return ONLY valid JSON with keys: ru, uz, en, tr. No markdown, no explanation.

Comment: {text}"""
    try:
        r = await client.chat.completions.create(
            model="gpt-4o-mini", temperature=0, max_tokens=400,
            messages=[
                {"role": "system", "content": "Construction translator. Return only JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        raw = r.choices[0].message.content.strip().strip("```json").strip("```").strip()
        data = json.loads(raw)
        return {l: data.get(l, text) for l in LANGS}
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return {l: text for l in LANGS}
