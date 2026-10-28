import unittest

from feedback_dedup import Feedback, deduplicate


class DeduplicateTests(unittest.TestCase):
    def test_related_feedback_forms_one_cluster(self):
        report = deduplicate([
            Feedback("a", "Export reports to CSV", votes=3),
            Feedback("b", "Please add CSV export for reports", votes=1),
            Feedback("c", "The dashboard color is hard to read"),
        ])
        self.assertEqual(report.item_count, 3)
        self.assertEqual(len(report.clusters), 2)
        self.assertEqual(set(report.clusters[0].item_ids), {"a", "b"})

    def test_urgent_terms_raise_priority(self):
        report = deduplicate([Feedback("a", "Users are blocked by a broken login", votes=2)])
        self.assertEqual(report.clusters[0].priority, "high")
        self.assertIn("urgent terms: blocked, broken", report.clusters[0].evidence)

    def test_invalid_threshold_and_empty_text_are_rejected(self):
        with self.assertRaises(ValueError):
            deduplicate([Feedback("a", "valid")], threshold=0)
        with self.assertRaises(ValueError):
            deduplicate([Feedback("a", " ")])

    def test_report_order_is_priority_first(self):
        report = deduplicate([
            Feedback("low", "Add a smaller avatar"),
            Feedback("high", "Security outage blocks checkout", votes=5),
        ])
        self.assertEqual(report.clusters[0].item_ids, ["high"])


if __name__ == "__main__":
    unittest.main()
