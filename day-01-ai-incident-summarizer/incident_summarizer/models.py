from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Event:
    timestamp: str
    service: str
    level: str
    message: str
    request_id: str | None = None
    region: str | None = None
    status_code: int | None = None
    affected_users: int = 0

    @property
    def is_failure(self) -> bool:
        return self.level.lower() in {"error", "critical", "fatal"} or (
            self.status_code is not None and self.status_code >= 500
        )


@dataclass
class IncidentReport:
    title: str
    severity: str
    score: int
    start: str
    end: str
    affected_users: int
    services: list[str]
    timeline: list[Event]
    signals: list[str] = field(default_factory=list)
    next_actions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "severity": self.severity,
            "score": self.score,
            "start": self.start,
            "end": self.end,
            "affected_users": self.affected_users,
            "services": self.services,
            "timeline": [event.__dict__ for event in self.timeline],
            "signals": self.signals,
            "next_actions": self.next_actions,
        }
