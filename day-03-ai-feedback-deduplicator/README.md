# AI Feedback Deduplicator

Product teams often receive the same request through surveys, support tickets, and interviews. This dependency-free utility groups similar feedback and ranks each theme with an explainable priority score, so a backlog can be triaged before sending text to an AI model or issue tracker.

## Features

- Groups related items with token Jaccard similarity; no model or API key is required.
- Selects a representative item and reports top keywords for every cluster.
- Scores urgency, community votes, and cluster size into low, medium, or high priority.
- Keeps evidence for each score and exposes a small Python library plus JSONL CLI.

## Run

Requires Python 3.10+ and no third-party packages.

```powershell
python -m feedback_dedup.cli examples\feedback.jsonl
python -m feedback_dedup.cli examples\feedback.jsonl --threshold 0.3 --json
python -m unittest discover -s tests -v
```

The CLI returns exit code 0 on success and 2 for invalid input. Lower thresholds create broader clusters; higher thresholds require more shared terms.

## Library example

```python
from feedback_dedup import Feedback, deduplicate

report = deduplicate([Feedback("a", "Add CSV export", votes=3)])
print(report.clusters[0].priority)
```

This is a transparent triage aid, not semantic understanding. Review clusters before automatically closing tickets or changing a product roadmap.
