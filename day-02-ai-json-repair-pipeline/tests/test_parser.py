import unittest

from json_repair import repair_response


class RepairResponseTests(unittest.TestCase):
    def test_strict_json_is_high_confidence_and_unchanged(self):
        result = repair_response('{"ok": true}', ["ok"])
        self.assertEqual(result.data, {"ok": True})
        self.assertEqual(result.confidence, "high")
        self.assertEqual(result.repairs, ())

    def test_fence_preamble_and_trailing_comma_are_explained(self):
        result = repair_response('Result:\n```json\n{"answer": "yes",}\n```', ["answer"])
        self.assertEqual(result.data["answer"], "yes")
        self.assertIn("removed markdown code fence", result.repairs)
        self.assertIn("removed trailing commas", result.repairs)

    def test_python_style_literals_fallback(self):
        result = repair_response("{'enabled': True, 'items': [1, 2]}")
        self.assertEqual(result.data["enabled"], True)
        self.assertIn("converted Python-style literals", result.repairs)

    def test_missing_required_field_is_low_confidence(self):
        result = repair_response('{"answer": "ok"}', ["answer", "score"])
        self.assertEqual(result.missing_fields, ("score",))
        self.assertEqual(result.confidence, "medium")

    def test_invalid_input_has_no_data(self):
        result = repair_response("not structured output")
        self.assertIsNone(result.data)
        self.assertEqual(result.confidence, "invalid")
        self.assertTrue(result.error)


if __name__ == "__main__":
    unittest.main()
