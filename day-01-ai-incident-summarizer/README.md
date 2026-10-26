# AI Incident Summarizer

Create a concise, explainable incident brief from JSONL service events. The tool groups related errors, builds a chronological timeline, estimates severity from impact signals, and suggests next actions. It is dependency-free and designed for local incident review or as a deterministic preprocessor before an LLM writes a richer postmortem.

## Structure

- `incident_summarizer/models.py` — typed event and report models
- `incident_summarizer/parser.py` — JSONL loading and validation
- `incident_summarizer/summarize.py` — grouping, scoring, timeline, and actions
- `incident_summarizer/cli.py` — text and JSON command-line output
- `examples/events.jsonl` — sample outage events
- `tests/` — automated behavior tests

## Run

Requires Python 3.10+ and no third-party packages.

```bash
python -m unittest discover -s tests -v
python -m incident_summarizer.cli examples/events.jsonl
python -m incident_summarizer.cli examples/events.jsonl --json
```

The input is one JSON object per line with `timestamp`, `service`, `level`, and `message`. Optional fields include `request_id`, `region`, `status_code`, and `affected_users`.

Severity and recommendations are rule-based and intentionally explainable; they are signals for review, not an autonomous diagnosis.
