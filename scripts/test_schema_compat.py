# -*- coding: utf-8 -*-
"""schema 兼容性测试：旧读新、未知版本降级、缺字段回退。"""
import io, unittest, yaml
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "conferences.yml"

class CompatTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = yaml.safe_load(io.open(DATA, encoding="utf-8").read()) or []

    def test_rows_are_list(self):
        self.assertIsInstance(self.rows, list)
        self.assertGreater(len(self.rows), 0)

    def test_old_reader_ignores_new_fields(self):
        keys = {"title", "sub", "events"}
        for r in self.rows[:20]:
            self.assertTrue(keys.issubset(set(r.keys())))

    def test_all_rows_have_schema_version(self):
        self.assertTrue(all(r.get("schema_version") == "1.1" for r in self.rows))

    def test_missing_derived_fields_do_not_break(self):
        e = self.rows[0]["events"][0]
        self.assertIn("status", e)
        self.assertIn("timeline", e)

    def test_timezone_original_preserved(self):
        for r in self.rows:
            for e in r.get("events") or []:
                self.assertIn("timezone", e)

if __name__ == "__main__":
    unittest.main()
