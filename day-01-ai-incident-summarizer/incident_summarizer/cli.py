import argparse
import json

from .parser import load_events
from .summarize import build_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an explainable incident brief from JSONL events.")
    parser.add_argument("events", help="path to JSONL events")
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit JSON")
    args = parser.parse_args()
    try:
        report = build_report(load_events(args.events))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    if args.as_json:
        print(json.dumps(report.to_dict(), indent=2))
        return 0
    print(f"{report.title} (score {report.score}/100)")
    print(f"Window: {report.start} → {report.end}")
    print(f"Services: {', '.join(report.services)} | Affected users: {report.affected_users:,}")
    print("Signals:")
    for signal in report.signals:
        print(f"- {signal}")
    print("Next actions:")
    for action in report.next_actions:
        print(f"- {action}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
