# AI JSON Repair Pipeline

LLM output is often almost JSON: it may be wrapped in Markdown fences, include a short preamble, or contain a trailing comma. This dependency-free utility extracts, repairs, and validates JSON-like responses while keeping an explainable repair trail.

## Features

- Strict JSON parsing first, so already-valid output is never changed.
- Extracts the first balanced object or array from surrounding prose.
- Repairs common trailing commas and Python-style literals.
- Validates required top-level fields and reports confidence plus warnings.
- Provides a small library and a CLI that emits human-readable or JSON output.

## Run

Requires Python 3.10+ and no third-party packages.

```powershell
python -m json_repair.cli examples\response.txt --required answer,score
python -m json_repair.cli examples\response.txt --required answer,score --json
python -m unittest discover -s tests -v
```

The CLI exits with status 0 when parsing and required-field validation succeed, and 1 when they do not.

## Library example

```python
from json_repair import repair_response

result = repair_response('```json\n{"answer": "yes", "score": 0.9,}\n```', ["answer", "score"])
print(result.data, result.repairs, result.confidence)
```

This is a repair-and-validation aid, not a security boundary. Treat repaired values as untrusted input and apply domain-specific type and range checks afterward.
