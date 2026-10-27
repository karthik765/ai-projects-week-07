"""Small, deterministic parser for almost-JSON model responses."""

from __future__ import annotations

import ast
import json
import re
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class RepairResult:
    data: Any | None
    repairs: tuple[str, ...]
    missing_fields: tuple[str, ...]
    confidence: str
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _balanced_candidate(text: str) -> str | None:
    starts = [i for i, char in enumerate(text) if char in "[{]"]
    for start in starts:
        opener = text[start]
        closer = "}" if opener == "{" else "]"
        depth = 0
        quote: str | None = None
        escaped = False
        for index in range(start, len(text)):
            char = text[index]
            if quote:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == quote:
                    quote = None
                continue
            if char in "\"'":
                quote = char
            elif char == opener:
                depth += 1
            elif char == closer:
                depth -= 1
                if depth == 0:
                    return text[start : index + 1]
    return None


def _remove_trailing_commas(text: str) -> str:
    return re.sub(r",\s*([}\]])", r"\1", text)


def repair_response(text: str, required_fields: list[str] | tuple[str, ...] = ()) -> RepairResult:
    """Parse text and record each normalization used along the way."""
    repairs: list[str] = []
    candidate = text.strip()
    try:
        data = json.loads(candidate)
    except json.JSONDecodeError as strict_error:
        if "```" in candidate:
            fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", candidate, re.IGNORECASE | re.DOTALL)
            if fenced:
                candidate = fenced.group(1).strip()
                repairs.append("removed markdown code fence")
        extracted = _balanced_candidate(candidate)
        if extracted and extracted != candidate:
            candidate = extracted
            repairs.append("extracted balanced JSON value")
        normalized = _remove_trailing_commas(candidate)
        if normalized != candidate:
            candidate = normalized
            repairs.append("removed trailing commas")
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError:
            try:
                data = ast.literal_eval(candidate)
                if not isinstance(data, (dict, list)):
                    raise ValueError("value is not an object or array")
                repairs.append("converted Python-style literals")
            except (ValueError, SyntaxError, TypeError) as fallback_error:
                return RepairResult(None, tuple(repairs), tuple(required_fields), "invalid", str(fallback_error or strict_error))

    missing = tuple(field for field in required_fields if not isinstance(data, dict) or field not in data)
    if missing:
        confidence = "low" if repairs else "medium"
    elif repairs:
        confidence = "medium"
    else:
        confidence = "high"
    return RepairResult(data, tuple(repairs), missing, confidence)
