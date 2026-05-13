import json
import logging
from openai import AsyncOpenAI
from config import OPENAI_API_KEY

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_TRANSLATE = """You are a professional construction industry translator.
Translate the given text into Uzbek (uz), English (en), and Turkish (tr).
Return ONLY valid JSON with keys: uz, en, tr.
Be literal and precise. Use construction terminology. No interpretation."""

SYSTEM_NORMALIZE = """You are a construction engineering assistant.
Normalize the given defect description to standard construction terminology in Russian.
Return ONLY the normalized Russian text, nothing else. Be concise (max 10 words)."""


async def translate_comment(text_ru: str) -> dict:
    """Translate Russian comment to uz, en, tr. Returns dict with keys uz/en/tr."""
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_TRANSLATE},
                {"role": "user", "content": f"Translate this construction note: {text_ru}"}
            ],
            max_tokens=300,
        )
        raw = response.choices[0].message.content.strip()
        # Strip markdown fences if present
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as e:
        logger.warning(f"GPT translation failed: {e}")
        return {"uz": text_ru, "en": text_ru, "tr": text_ru}


async def translate_term(text_ru: str) -> dict:
    """Auto-translate a new reference term from Russian to uz/en/tr."""
    return await translate_comment(text_ru)


async def normalize_defect(text: str, lang: str) -> str:
    """Normalize free-text defect description in given language to Russian standard term."""
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_NORMALIZE},
                {"role": "user", "content": f"Language: {lang}. Defect: {text}"}
            ],
            max_tokens=50,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.warning(f"GPT normalization failed: {e}")
        return text
