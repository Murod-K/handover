"""
Translation service using OpenAI GPT.
ONLY used for free-text comments — not for structured data.
Principle: verbatim translation, temperature=0, no interpretation.
"""

import json
import logging
from openai import AsyncOpenAI
from config import Config

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=Config().OPENAI_API_KEY)

TARGET_LANGUAGES = ["ru", "uz", "en", "tr"]
LANG_NAMES = {
    "ru": "Russian",
    "uz": "Uzbek",
    "en": "English",
    "tr": "Turkish"
}


async def translate_comment(text: str, source_lang: str = "ru") -> dict[str, str]:
    """
    Translate a user comment to all 4 languages.
    Returns dict: {lang_code: translated_text}
    """
    if not text or not text.strip():
        return {lang: "" for lang in TARGET_LANGUAGES}

    prompt = f"""Translate the following construction site comment VERBATIM into these languages:
Russian, Uzbek, English, Turkish.

Rules:
- Do NOT add any commentary, explanation, or extra words
- Do NOT interpret the meaning — translate literally
- Preserve technical terms as close as possible
- Return ONLY a JSON object with keys: ru, uz, en, tr

Comment to translate:
{text}

Return JSON only, no markdown:"""

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            max_tokens=500,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional construction-industry translator. Return only valid JSON."
                },
                {"role": "user", "content": prompt}
            ]
        )
        raw = response.choices[0].message.content.strip()
        # Strip markdown if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        translations = json.loads(raw.strip())
        return {lang: translations.get(lang, text) for lang in TARGET_LANGUAGES}
    except Exception as e:
        logger.error(f"Translation error: {e}")
        # Fallback: return original for all
        return {lang: text for lang in TARGET_LANGUAGES}
