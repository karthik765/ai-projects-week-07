"""Command-line entry point for the JSON repair pipeline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .parser import repair_response


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Repair and validate almost-JSON model output")
    parser.add_argument("input", type=Path, help="text file containing the model response")
    parser.add_argument("--required", default="", help="comma-separated required top-level fields")
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit machine-readable output")
    args = parser.parse_args(argv)
    result = repair_response(args.input.read_text(encoding="utf-8"), [x for x in args.required.split(",") if x])
    payload = result.to_dict()
    if args.as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"confidence: {result.confidence}")
        print(f"data: {json.dumps(result.data, ensure_ascii=False)}")
        print(f"repairs: {', '.join(result.repairs) or 'none'}")
        print(f"missing fields: {', '.join(result.missing_fields) or 'none'}")
        if result.error:
            print(f"error: {result.error}")
    return 0 if result.data is not None and not result.missing_fields else 1


if __name__ == "__main__":
    sys.exit(main())
