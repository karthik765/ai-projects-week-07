from collections import Counter

from .models import Event, IncidentReport


def _severity(score: int) -> str:
    return "critical" if score >= 80 else "high" if score >= 55 else "medium" if score >= 25 else "low"


def build_report(events: list[Event]) -> IncidentReport:
    ordered = sorted(events, key=lambda event: event.timestamp)
    failures = [event for event in ordered if event.is_failure]
    services = sorted({event.service for event in failures or ordered})
    users = max((event.affected_users for event in ordered), default=0)
    score = min(100, len(failures) * 12 + (35 if users >= 1000 else 20 if users else 0) + (20 if any(e.status_code == 503 for e in failures) else 0))
    signals = []
    if failures:
        signals.append(f"{len(failures)} failure event(s) across {len(services)} service(s)")
    if users:
        signals.append(f"reported impact reached {users:,} users")
    regions = sorted({event.region for event in failures if event.region})
    if regions:
        signals.append(f"failure regions: {', '.join(regions)}")
    codes = Counter(event.status_code for event in failures if event.status_code)
    if codes:
        signals.append("status codes: " + ", ".join(f"{code} ({count})" for code, count in sorted(codes.items())))
    actions = ["Confirm the first failing dependency and preserve correlated request IDs."]
    if any(event.status_code == 503 for event in failures):
        actions.insert(0, "Check capacity, saturation, and upstream availability for 503 responses.")
    if users >= 1000:
        actions.append("Open incident communications and record the affected-user estimate.")
    title = f"{_severity(score).title()} incident involving {', '.join(services[:3])}"
    return IncidentReport(title, _severity(score), score, ordered[0].timestamp, ordered[-1].timestamp, users, services, ordered, signals, actions)
