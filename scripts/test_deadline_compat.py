# -*- coding: utf-8 -*-
"""双轨日期兼容解析的正反用例。"""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from deadline_compat import parse_deadline, to_iso


class CompatTest(unittest.TestCase):
    def test_legacy_space(self):
        self.assertEqual(parse_deadline("2026-01-05 23:59:59").year, 2026)

    def test_iso_t(self):
        self.assertEqual(parse_deadline("2026-01-05T23:59:59").second, 59)

    def test_date_only(self):
        self.assertEqual(parse_deadline("2026-01-05").day, 5)

    def test_tbd_and_none(self):
        self.assertIsNone(parse_deadline("TBD"))
        self.assertIsNone(parse_deadline(None))
        self.assertIsNone(parse_deadline(""))

    def test_invalid(self):
        self.assertIsNone(parse_deadline("NOT-A-DATE"))

    def test_to_iso(self):
        self.assertEqual(to_iso("2026-01-05 23:59:59"), "2026-01-05T23:59:59")
        self.assertEqual(to_iso("TBD"), "TBD")


if __name__ == "__main__":
    unittest.main()
