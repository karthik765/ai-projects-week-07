import argparse
import json
import sys

from .deduplicate import deduplicate
from .models import Feedback


def _load(path: str) -> list[Feedback]:
    items = []
    with open(path, encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
                items.append(Feedback(str(value["id"]), str(value["text"]),
                                      str(value.get("source", "unknown")), int(value.get("votes", 0))))
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                raise ValueError(f"invalid JSONL at line {line_number}: {exc}") from exc
    return items


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Cluster duplicate product feedback.")
    parser.add_argument("input", help="JSONL file with id, text, source, and optional votes")
    parser.add_argument("--threshold", type=float, default=0.35)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    try:
        report = deduplicate(_load(args.input), args.threshold)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    payload = {"item_count": report.item_count, "clusters": [cluster.__dict__ for cluster in report.clusters]}
    if args.as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"{report.item_count} items -> {len(report.clusters)} clusters")
        for cluster in report.clusters:
            print(f"\n#{cluster.id} [{cluster.priority}] {cluster.representative}")
            print(f"  items: {', '.join(cluster.item_ids)}")
            print(f"  keywords: {', '.join(cluster.keywords)}")
            print(f"  score: {cluster.score:.1f} | {'; '.join(cluster.evidence)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
