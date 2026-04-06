import json
from typing import Any

import httpx

from app.core.config import settings
from app.services.text_normalizer import normalize_hinglish_text


def _extract_text(payload: dict[str, Any]) -> str:
    output_text = payload.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    parts: list[str] = []
    for item in payload.get("output", []):
        for content in item.get("content", []):
            text = content.get("text")
            if isinstance(text, str):
                parts.append(text)
    return "\n".join(parts).strip()


async def refine_hinglish_text(text: str) -> str:
    if not text.strip():
        return text

    if not settings.enable_hinglish_refiner:
        return normalize_hinglish_text(text)

    if settings.llm_provider != "openai" or not settings.openai_api_key:
        return normalize_hinglish_text(text)

    prompt = {
        "instruction": (
            "Rewrite this tutoring text into natural Hindi+English mixed style. "
            "Use Devanagari for Hindi words. Keep technical/software terms in English. "
            "Keep original meaning and roughly similar length. Return plain text only."
        ),
        "text": text,
    }

    body = {
        "model": settings.hinglish_refiner_model or settings.openai_model,
        "temperature": 0.2,
        "input": [
            {
                "role": "user",
                "content": [{"type": "input_text", "text": json.dumps(prompt, ensure_ascii=False)}],
            }
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.post(
                "https://api.openai.com/v1/responses",
                headers={
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": "application/json",
                },
                json=body,
            )
            response.raise_for_status()
            payload = response.json()

        refined = _extract_text(payload)
        if not refined:
            return normalize_hinglish_text(text)
        return normalize_hinglish_text(refined)
    except Exception:
        return normalize_hinglish_text(text)


async def refine_hinglish_list(values: list[str]) -> list[str]:
    out: list[str] = []
    for value in values:
        out.append(await refine_hinglish_text(value))
    return out
