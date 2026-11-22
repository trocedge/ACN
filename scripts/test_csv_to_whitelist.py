# -*- coding: utf-8 -*-
"""csv_to_whitelist 的正反用例，用临时目录隔离，不污染正式数据。"""
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from csv_to_whitelist import (parse_csv_rows, merge_and_validate,
                              serialize_items, read_header_block)

COMPETITION = ROOT / "competition"


def load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


class CsvToWhitelistTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.types = load(COMPETITION / "types.yml")
        cls.whitelist = load(COMPETITION / "whitelist.yml")

    def _write_csv(self, text: str) -> Path:
        f = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8-sig", newline="")
        f.write(text)
        f.close()
        return Path(f.name)

    def test_parse_csv_rows_ok(self):
        csv_path = self._write_csv(
            "seq,title,sub,category,site,deadline,timezone,source_url\n"
            "3,,,,https://example.org/,,,\n"
            "85,全国测试竞赛,CS,计算机类,https://example.org/,,,\n"
        )
        rows, errors = parse_csv_rows(csv_path)
        self.assertEqual(errors, [])
        self.assertEqual(len(rows), 2)
        # 第一行只填 seq 和 site，其余省略
        self.assertEqual(rows[0][1], {"seq": "3", "site": "https://example.org/"})

    def test_normal_merge_updates_and_appends(self):
        existing = load(COMPETITION / "whitelist.yml")
        rows = [
            (2, {"seq": "3", "site": "https://new.example.org/"}),
            (3, {"seq": "85", "title": "全国测试竞赛", "sub": "CS",
                 "category": "计算机类", "site": "https://example.org/"}),
        ]
        merged, added, updated, errors = merge_and_validate(existing, self.types, rows)
        self.assertEqual(errors, [])
        self.assertIn(3, updated)
        self.assertIn(85, added)
        self.assertEqual(len(merged), len(existing) + 1)
        by_seq = {i["seq"]: i for i in merged}
        self.assertEqual(by_seq[3]["site"], "https://new.example.org/")
        self.assertEqual(by_seq[85]["title"], "全国测试竞赛")

    def test_bad_deadline_reported_with_row_number(self):
        existing = load(COMPETITION / "whitelist.yml")
        rows = [
            (2, {"seq": "1", "deadline": "三月底", "source_url": "https://example.org/"}),
        ]
        merged, added, updated, errors = merge_and_validate(existing, self.types, rows)
        self.assertTrue(errors)
        self.assertTrue(any("第 2 行" in e for e in errors))

    def test_dup_seq_in_csv_reported(self):
        existing = load(COMPETITION / "whitelist.yml")
        rows = [
            (2, {"seq": "85", "title": "A", "sub": "CS", "category": "计算机类", "site": "https://a.example.org/"}),
            (3, {"seq": "85", "title": "B", "sub": "CS", "category": "计算机类", "site": "https://b.example.org/"}),
        ]
        merged, added, updated, errors = merge_and_validate(existing, self.types, rows)
        self.assertTrue(any("重复" in e for e in errors))

    def test_extend_beyond_84_passes(self):
        existing = load(COMPETITION / "whitelist.yml")
        rows = [
            (2, {"seq": "85", "title": "全国测试竞赛", "sub": "CS",
                 "category": "计算机类", "site": "https://example.org/"}),
        ]
        merged, added, updated, errors = merge_and_validate(existing, self.types, rows)
        self.assertEqual(errors, [])
        self.assertEqual(added, [85])

    def test_serialize_roundtrip(self):
        # 序列化后能被 yaml 无损读回，且字段值不变
        text = serialize_items(self.whitelist)
        back = yaml.safe_load(text)
        self.assertEqual(back, self.whitelist)

    def test_header_block_kept(self):
        header = read_header_block(COMPETITION / "whitelist.yml")
        self.assertTrue(header.startswith("#"))
        self.assertIn("教育部认可", header)


if __name__ == "__main__":
    unittest.main()
