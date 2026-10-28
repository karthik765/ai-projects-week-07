from collections import Counter

from .models import Cluster, Feedback, Report
from .normalize import similarity, tokens

URGENT = {"down", "outage", "broken", "blocked", "cannot", "can't", "security", "lost"}
POSITIVE = {"love", "great", "helpful", "easy", "fast"}


def _priority(items: list[Feedback], keywords: list[str]) -> tuple[str, float, list[str]]:
    joined = set(keywords)
    votes = sum(max(item.votes, 0) for item in items)
    urgent_hits = sorted(joined & URGENT)
    score = min(100.0, 20.0 * len(urgent_hits) + min(votes, 10) * 3.0 + len(items) * 8.0)
    evidence = []
    if urgent_hits:
        evidence.append("urgent terms: " + ", ".join(urgent_hits))
    if votes:
        evidence.append(f"community votes: {votes}")
    evidence.append(f"similar items: {len(items)}")
    return ("high" if score >= 50 else "medium" if score >= 30 else "low", score, evidence)


def deduplicate(items: list[Feedback], threshold: float = 0.35) -> Report:
    """Group feedback using transparent token Jaccard similarity."""
    if threshold <= 0 or threshold > 1:
        raise ValueError("threshold must be greater than 0 and at most 1")
    groups: list[list[Feedback]] = []
    for item in items:
        if not item.text.strip():
            raise ValueError(f"feedback {item.id!r} has empty text")
        match = next((group for group in groups if any(
            similarity(item.text, existing.text) >= threshold for existing in group
        )), None)
        if match is None:
            groups.append([item])
        else:
            match.append(item)

    clusters = []
    for index, group in enumerate(groups, 1):
        representative = max(group, key=lambda item: (item.votes, len(item.text))).text
        counts = Counter(token for item in group for token in tokens(item.text))
        keywords = [word for word, _ in counts.most_common(5)]
        priority, score, evidence = _priority(group, keywords)
        clusters.append(Cluster(index, [item.id for item in group], representative,
                                keywords, round(score, 1), priority, evidence))
    clusters.sort(key=lambda cluster: (-cluster.score, cluster.id))
    for index, cluster in enumerate(clusters, 1):
        cluster.id = index
    return Report(clusters=clusters, unclustered=[], item_count=len(items))

