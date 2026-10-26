import json
import unittest

from incident_summarizer.parser import parse_lines
from incident_summarizer.summarize import build_report


class IncidentSummarizerTests(unittest.TestCase):
    def test_report_orders_events_and_detects_high_impact(self):
        events = parse_lines([
            json.dumps({"timestamp": "2026-10-26T10:02:00Z", "service": "api", "level": "error", "message": "upstream unavailable", "status_code": 503, "affected_users": 1200, "region": "us-east"}),
            json.dumps({"timestamp": "2026-10-26T10:01:00Z", "service": "api", "level": "info", "message": "deploy started"}),
        ])
        report = build_report(events)
        self.assertEqual(report.start, "2026-10-26T10:01:00Z")
        self.assertEqual(report.severity, "high")
        self.assertEqual(report.affected_users, 1200)
        self.assertIn("capacity", report.next_actions[0])

    def test_success_events_still_produce_a_low_signal_report(self):
        events = parse_lines([json.dumps({"timestamp": "2026-10-26T10:00:00Z", "service": "web", "level": "info", "message": "healthy"})])
        report = build_report(events)
        self.assertEqual(report.severity, "low")
        self.assertEqual(report.services, ["web"])

    def test_parser_rejects_missing_fields_and_bad_json(self):
        with self.assertRaisesRegex(ValueError, "missing message"):
            parse_lines(['{"timestamp":"x","service":"api","level":"error"}'])
        with self.assertRaisesRegex(ValueError, "invalid JSON"):
            parse_lines(["not-json"])

    def test_report_is_serializable(self):
        events = parse_lines([json.dumps({"timestamp": "x", "service": "api", "level": "error", "message": "failed", "request_id": "r1"})])
        payload = build_report(events).to_dict()
        self.assertEqual(payload["timeline"][0]["request_id"], "r1")


if __name__ == "__main__":
    unittest.main()
