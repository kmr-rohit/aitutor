import json
from typing import Any

import httpx

from app.providers.base import LLMProvider, LLMResult


def _extract_text(body: dict[str, Any]) -> str:
    output_text = body.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    parts: list[str] = []
    for item in body.get("output", []):
        for content in item.get("content", []):
            text = content.get("text")
            if isinstance(text, str):
                parts.append(text)
    return "\n".join(parts).strip()


def _extract_json_blob(text: str) -> dict[str, Any] | None:
    raw = text.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:].strip()

    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    start = raw.find("{")
    end = raw.rfind("}")
    if start >= 0 and end > start:
        try:
            parsed = json.loads(raw[start : end + 1])
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            return None
    return None


def _compact_context(context: list[dict], max_turns: int = 4, max_chars: int = 900) -> list[str]:
    items: list[str] = []
    for turn in context[-max_turns:]:
        role = str(turn.get("role", "user"))
        text = str(turn.get("text", "")).strip()
        if not text:
            continue
        if len(text) > 260:
            text = f"{text[:260]}..."
        items.append(f"{role}: {text}")
    merged = "\n".join(items)
    if len(merged) > max_chars:
        merged = merged[-max_chars:]
    return merged.splitlines() if merged else []


class OpenAILLMProvider(LLMProvider):
    def __init__(self, api_key: str, model: str, timeout_seconds: float):
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds

    async def respond(self, context: list[dict], mode: str, rubric: dict) -> LLMResult:
        latest = context[-1].get("text", "") if context else ""
        if len(latest) > 500:
            latest = f"{latest[:500]}..."
        compact_context = _compact_context(context)
        prompt = {
            "mode": mode,
            "rubric": rubric,
            "latest_question": latest,
            "recent_context": compact_context,
        }

        system = (
            "You are a warm interview-prep tutor. Reply in simple Hinglish (Hindi-English mixed). "
            "For common Hindi words, prefer Devanagari script where natural "
            "(e.g., मतलब, ज़्यादा, क्यों, अगर, लेकिन). "
            "Return strict JSON with keys: answer (string), hints (array of 2 strings), "
            "followups (array of 1-2 strings)."
        )

        url = "https://api.openai.com/v1/responses"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        input_obj = [
            {
                "role": "system",
                "content": [{"type": "input_text", "text": system}],
            },
            {
                "role": "user",
                "content": [{"type": "input_text", "text": json.dumps(prompt, ensure_ascii=False)}],
            },
        ]
        input_string = (
            f"{system}\n\n"
            f"Mode: {mode}\n"
            f"Rubric: {json.dumps(rubric, ensure_ascii=False)}\n"
            f"Latest question: {latest}\n"
            f"Recent context: {json.dumps(compact_context, ensure_ascii=False)}"
        )

        payloads = [
            {"model": self.model, "temperature": 0.4, "input": input_obj},
            {"model": self.model, "input": input_obj},
            {"model": self.model, "input": input_string},
        ]

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            payload = None
            last_error: str | None = None
            for body in payloads:
                response = await client.post(url, headers=headers, json=body)
                if response.is_success:
                    payload = response.json()
                    break
                if response.status_code == 400:
                    last_error = response.text
                    continue
                response.raise_for_status()

            if payload is None:
                raise RuntimeError(f"OpenAI responses failed with 400: {last_error or 'bad_request'}")

        text = _extract_text(payload)
        parsed = _extract_json_blob(text) or {}

        answer = parsed.get("answer") if isinstance(parsed.get("answer"), str) else text
        hints_raw = parsed.get("hints") if isinstance(parsed.get("hints"), list) else []
        followups_raw = parsed.get("followups") if isinstance(parsed.get("followups"), list) else []

        hints = [str(x) for x in hints_raw if str(x).strip()][:2]
        followups = [str(x) for x in followups_raw if str(x).strip()][:2]

        if not hints:
            hints = ["Requirements clear karo", "Tradeoffs explicitly explain karo"]
        if not followups:
            followups = ["Is design ka bottleneck kya ho sakta hai?"]

        return LLMResult(answer=answer, hints=hints, followups=followups)
