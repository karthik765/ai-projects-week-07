import re

STOPWORDS = {
    "a", "an", "and", "are", "be", "but", "for", "from", "has", "have",
    "i", "in", "is", "it", "my", "of", "on", "or", "our", "the", "to",
    "very", "was", "we", "with", "would", "you", "your",
}


def tokens(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [word for word in words if word not in STOPWORDS and len(word) > 2]


def similarity(left: str, right: str) -> float:
    a, b = set(tokens(left)), set(tokens(right))
    return len(a & b) / len(a | b) if a and b else 0.0

