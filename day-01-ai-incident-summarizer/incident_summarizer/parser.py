import json
from pathlib import Path
from typing import Iterable

from .models import Event


def parse_event(raw: dict, line_number: int) -> Event:
    required = ("timestamp", "service", "level", "message")
    missing = [key for key in required if not raw.get(key)]
    if missing:
        raise ValueError(f"line {line_number}: missing {', '.join(missing)}")
    affected = raw.get("affected_users", 0)
    if not isinstance(affected, int) or affected < 0:
        raise ValueError(f"line {line_number}: affected_users must be a non-negative integer")
    status = raw.get("status_code")
    if status is not None and (not isinstance(status, int) or not 100 <= status <= 599):
        raise ValueError(f"line {line_number}: status_code must be an HTTP status")
    return Event(
        timestamp=str(raw["timestamp"]), service=str(raw["service"]),
        level=str(raw["level"]), message=str(raw["message"]),
        request_id=raw.get("request_id"), region=raw.get("region"),
        status_code=status, affected_users=affected,
    )


def parse_lines(lines: Iterable[str]) -> list[Event]:
    events = []
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"line {number}: invalid JSON ({exc.msg})") from exc
        if not isinstance(value, dict):
            raise ValueError(f"line {number}: expected a JSON object")
        events.append(parse_event(value, number))
    if not events:
        raise ValueError("input contains no events")
    return events


def load_events(path: str | Path) -> list[Event]:
    with Path(path).open(encoding="utf-8") as handle:
        return parse_lines(handle)
