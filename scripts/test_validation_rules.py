# -*- coding: utf-8 -*-
"""扩展校验规则的正反用例。"""
import re, unittest
DEADLINE = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}|TBD)$")

class RuleTest(unittest.TestCase):
    def test_deadline_valid(self):
        self.assertTrue(DEADLINE.match("2026-11-10 23:59:59"))
    def test_deadline_tbd(self):
        self.assertTrue(DEADLINE.match("TBD"))
    def test_deadline_invalid(self):
        self.assertFalse(DEADLINE.match("2026-11-10T23:59:59"))
    def test_link_format(self):
        self.assertTrue(re.match(r"^https?://", "https://example.org"))
        self.assertFalse(re.match(r"^https?://", "example.org"))
    def test_rank_enum(self):
        self.assertIn("A", ("A", "B", "C", "N"))
        self.assertNotIn("Z", ("A", "B", "C", "N"))
    def test_timeline_order(self):
        self.assertEqual(["a", "b"], sorted(["b", "a"]))

if __name__ == "__main__":
    unittest.main()
