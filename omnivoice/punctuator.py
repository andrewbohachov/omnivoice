"""
OmniVoice - Smart Punctuation & IT Entity Enhancer
Restores grammatical punctuation (commas, sentence capitalization) and technical terms.
Zero emojis.
"""

import re

DEV_MAP = {
    r"\b(антигравити)\b": "Antigravity",
    r"\b(клоди[яею]|клод[ауе]?)\b": "Claude",
    r"\b(кодекс[еау]?)\b": "Codex",
    r"\b(гит[еау]?)\b": "Git",
    r"\b(гитхаб[еау]?)\b": "GitHub",
    r"\b(пулл?\s*реквест[ауе]?)\b": "Pull Request",
    r"\b(пуш\s*ту\s*то[л]?к)\b": "Push-to-Talk",
    r"\b(пайтон[еау]?|питон[еау]?)\b": "Python",
    r"\b(баш[еау]?)\b": "bash",
    r"\b(докер[еау]?)\b": "Docker",
    r"\b(апи)\b": "API",
    r"\b(цли|кли)\b": "CLI",
}

CONJUNCTIONS = [
    r"\bа\b", r"\bно\b", r"\bчто\b", r"\bчтобы\b", r"\bкак\b",
    r"\bесли\b", r"\bкогда\b", r"\bпотому что\b", r"\bтак как\b",
    r"\bхотя\b", r"\bкоторы[йяехм]+\b", r"\bгде\b", r"\bкуда\b",
    r"\bоткуда\b", r"\bто есть\b", r"\bто бишь\b"
]

INTRO_WORDS = [
    r"\bв общем-то\b", r"\bв общем\b", r"\bкороче говоря\b", r"\bкороче\b",
    r"\bкстати\b", r"\bпожалуйста\b", r"\bнаверное\b", r"\bпожалуй\b",
    r"\bк слову\b"
]

def enhance_text(text: str) -> str:
    if not text:
        return ""
    res = text.strip()

    # Punctuate introductory words
    for intro in INTRO_WORDS:
        word = intro.replace(r"\b", "")
        res = re.sub(rf"(?i)^{re.escape(word)}\s+", f"{word.capitalize()}, ", res)
        res = re.sub(rf"(?i)\s+{re.escape(word)}\s+", f", {word}, ", res)

    # Insert commas before subordinate conjunctions
    for conj in CONJUNCTIONS:
        c = conj.replace(r"\b", "")
        res = re.sub(rf"(?i)(?<![,\.!\?])\s+{re.escape(c)}\b", f", {c}", res)

    # Normalize technical and developer entities
    for pattern, repl in DEV_MAP.items():
        res = re.sub(pattern, repl, res, flags=re.IGNORECASE)

    # Clean double commas and spaces
    res = re.sub(r",\s*,+", ",", res)
    res = re.sub(r"\s*,\s*", ", ", res)
    res = re.sub(r"^,\s*", "", res)

    # Capitalize after sentence ends
    res = re.sub(r"(^|[\.\?!]\s+)([a-zа-яё])", lambda m: m.group(1) + m.group(2).upper(), res)

    return res.strip()
