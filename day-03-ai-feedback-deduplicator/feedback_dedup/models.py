from dataclasses import dataclass, field


@dataclass(frozen=True)
class Feedback:
    """One feedback item supplied by a customer or internal reviewer."""

    id: str
    text: str
    source: str = "unknown"
    votes: int = 0


@dataclass
class Cluster:
    id: int
    item_ids: list[str]
    representative: str
    keywords: list[str]
    score: float
    priority: str
    evidence: list[str] = field(default_factory=list)


@dataclass
class Report:
    clusters: list[Cluster]
    unclustered: list[str]
    item_count: int

