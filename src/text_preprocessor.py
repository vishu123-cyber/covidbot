import re
from typing import List


def preprocess_text(text: str) -> str:
    """Lowercase and normalize user text."""
    if not isinstance(text, str):
        return ""

    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s\-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize_text(text: str) -> List[str]:
    """Convert a sentence into cleaned tokens."""
    cleaned = preprocess_text(text)
    return [token for token in cleaned.split() if token]