"""Explainable incident summarization from structured service events."""

from .models import Event, IncidentReport
from .parser import load_events
from .summarize import build_report

__all__ = ["Event", "IncidentReport", "load_events", "build_report"]
