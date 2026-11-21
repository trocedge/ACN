# -*- coding: utf-8 -*-
"""竞赛数据校验器的正反用例，夹具位于 tests/fixtures/competition/。"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import yaml

from validate_competition import validate_items

FIXTURES = ROOT / "tests" / "fixtures" / "competition"
TYPES = ROOT / "competition" / "types.yml"


def load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


class CompetitionValidationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.types = load(TYPES)

    def check_fails(self, fixture: str, keyword: str) -> None:
        errors = validate_items(load(FIXTURES / fixture), self.types, strict_count=False)
        self.assertTrue(errors, f"{fixture} 应校验失败")
        self.assertTrue(
            any(keyword in e for e in errors),
            f"{fixture} 的报错应包含 {keyword!r}，实际: {errors}",
        )

    def test_valid_fixture_passes(self):
        errors = validate_items(load(FIXTURES / "valid.yml"), self.types, strict_count=False)
        self.assertEqual(errors, [])

    def test_valid_fixture_passes_with_strict_count(self):
        # 夹具只有 2 项，开严格序号检查必然失败，验证开关本身生效
        errors = validate_items(load(FIXTURES / "valid.yml"), self.types, strict_count=True)
        self.assertTrue(any("连续" in e for e in errors))

    def test_duplicate_seq(self):
        self.check_fails("dup_seq.yml", "重复")

    def test_unknown_sub(self):
        self.check_fails("unknown_sub.yml", "不在 types.yml")

    def test_deadline_without_source(self):
        self.check_fails("missing_source.yml", "source_url")

    def test_empty_title(self):
        self.check_fails("empty_title.yml", "title")

    def test_bad_deadline_format(self):
        items = [{"seq": 1, "title": "测试", "sub": "COMP", "category": "综合类",
                  "deadline": "大概三月底"}]
        errors = validate_items(items, self.types, strict_count=False)
        self.assertTrue(any("ISO 8601" in e for e in errors))

    def test_bad_deadline_date(self):
        items = [{"seq": 1, "title": "测试", "sub": "COMP", "category": "综合类",
                  "deadline": "2027-02-30T00:00:00",
                  "source_url": "https://example.org/"}]
        errors = validate_items(items, self.types, strict_count=False)
        self.assertTrue(any("日期不存在" in e for e in errors))

    def test_bad_site(self):
        items = [{"seq": 1, "title": "测试", "sub": "COMP", "category": "综合类",
                  "site": "example.org"}]
        errors = validate_items(items, self.types, strict_count=False)
        self.assertTrue(any("site" in e for e in errors))

    def test_official_whitelist_passes(self):
        items = load(ROOT / "competition" / "whitelist.yml")
        errors = validate_items(items, self.types, strict_count=True)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
