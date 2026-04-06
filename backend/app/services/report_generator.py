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


def _fallback_report(topic: str, turns: list[dict]) -> str:
    learner_questions = [t.get("text", "") for t in turns if t.get("role") == "learner"][-5:]
    q_lines = "\n".join(f"- {q}" for q in learner_questions if q) or "- Session conversation available"
    return normalize_hinglish_text(
        "Detailed coaching report:\n"
        f"Topic: {topic}\n\n"
        "1) Concept Summary\n"
        "- Core system ko requirements, scale, aur failure points ke saath explain karna hai.\n\n"
        "2) Worked Example\n"
        "- Example: URL shortener me write path (API -> ID generation -> DB), read path (cache -> DB fallback).\n\n"
        "3) Your Questions Reviewed\n"
        f"{q_lines}\n\n"
        "4) Improvement Suggestions\n"
        "- हर answer ke start me assumptions bolo.\n"
        "- Tradeoffs ko latency, cost, aur complexity me quantify karo.\n"
        "- Bottleneck and failure recovery explicitly mention karo."
    )


async def generate_deep_report(topic: str, turns: list[dict]) -> str:
    if not settings.enable_deep_report:
        return _fallback_report(topic, turns)

    if settings.llm_provider != "openai" or not settings.openai_api_key:
        return _fallback_report(topic, turns)

    compact_turns = []
    for turn in turns[-10:]:
        text = str(turn.get("text", "")).strip()
        if not text:
            continue
        if len(text) > 240:
            text = f"{text[:240]}..."
        compact_turns.append({"role": turn.get("role", "user"), "text": text})

    prompt = {
        "topic": topic,
        "conversation": compact_turns,
        "instruction": (
            "Create an in-depth interview coaching report in natural Hindi+English mix. "
            "Use Devanagari for Hindi words, English for technical terms. "
            "Include: concept summary, 2 concrete examples, mistakes observed, model answers, "
            "and a 20-minute practice drill. Return plain text only."
        ),
    }

    body = {
        "model": settings.deep_report_model or settings.openai_model,
        "temperature": 0.3,
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

        report = _extract_text(payload)
        if not report:
            return _fallback_report(topic, turns)
        return normalize_hinglish_text(report)
    except Exception:
        return _fallback_report(topic, turns)
