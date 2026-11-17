# -*- coding: utf-8 -*-
"""从产出与校验报告生成 docs/stats.md，避免文档数字过期。"""
import io, sys, yaml, json
from datetime import datetime
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "conferences.yml"
REPORT = ROOT / "docs" / "data-validation-report.json"
OUT = ROOT / "docs" / "stats.md"

def main():
    rows = yaml.safe_load(io.open(DATA, encoding="utf-8").read()) or []
    events = [e for r in rows for e in (r.get("events") or [])]
    points = [p for e in events for p in (e.get("timeline") or [])]
    rep = json.loads(io.open(REPORT, encoding="utf-8").read()) if REPORT.is_file() else {}
    lines = ["# 数据统计（自动生成，请勿手改）", "",
             "- 生成时间：%s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             "- 来源：`data/conferences.yml`、`docs/data-validation-report.json`", "",
             "| 指标 | 数值 |", "|---|---:|",
             "| 会议条目 | %d |" % len(rows),
             "| 届次 events | %d |" % len(events),
             "| 时间节点 | %d |" % len(points),
             "| 校验 ERROR | %s |" % rep.get("errors", "无报告"),
             "| 校验 WARN | %s |" % rep.get("warnings", "无报告"),
             "| schema 版本 | %s |" % (rows[0].get("schema_version") if rows else "?"), ""]
    io.open(OUT, "w", encoding="utf-8").write("\n".join(lines))
    print("已生成", OUT)
    return 0

if __name__ == "__main__":
    sys.exit(main())
