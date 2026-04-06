import re

# Common Roman Hindi words we want to render in Devanagari for better readability.
REPLACEMENTS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bmatlab\b", re.IGNORECASE), "मतलब"),
    (re.compile(r"\bmtlb\b", re.IGNORECASE), "मतलब"),
    (re.compile(r"\bzyada\b", re.IGNORECASE), "ज़्यादा"),
    (re.compile(r"\bjyada\b", re.IGNORECASE), "ज़्यादा"),
    (re.compile(r"\bbahut\b", re.IGNORECASE), "बहुत"),
    (re.compile(r"\bkyu\b", re.IGNORECASE), "क्यों"),
    (re.compile(r"\bkyun\b", re.IGNORECASE), "क्यों"),
    (re.compile(r"\bkaise\b", re.IGNORECASE), "कैसे"),
    (re.compile(r"\bagar\b", re.IGNORECASE), "अगर"),
    (re.compile(r"\blekin\b", re.IGNORECASE), "लेकिन"),
    (re.compile(r"\bsamjho\b", re.IGNORECASE), "समझो"),
    (re.compile(r"\bsamjhte\b", re.IGNORECASE), "समझते"),
    (re.compile(r"\bsawal\b", re.IGNORECASE), "सवाल"),
]


def normalize_hinglish_text(text: str) -> str:
    out = text
    for pattern, replacement in REPLACEMENTS:
        out = pattern.sub(replacement, out)
    return out


def normalize_list(values: list[str]) -> list[str]:
    return [normalize_hinglish_text(v) for v in values]
