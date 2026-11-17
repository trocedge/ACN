# -*- coding: utf-8 -*-
"""schema 1.0 -> 1.1 迁移：补齐新增字段，幂等，支持 --dry。"""
import argparse, io, sys, yaml
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "conferences.yml"

def migrate(rows):
    changed = 0
    for r in rows:
        if r.get("schema_version") != "1.1":
            r["schema_version"] = "1.1"; changed += 1
        for e in r.get("events") or []:
            for key, default in (("status", "unknown"), ("status_basis", "none"),
                                 ("date_zh", None), ("place_zh", None),
                                 ("timezone_utc_offset", None), ("sort_key", None)):
                if key not in e:
                    e[key] = default; changed += 1
            for p in e.get("timeline") or []:
                if "deadline_beijing" not in p:
                    p["deadline_beijing"] = None; changed += 1
    return rows, changed

def main():
    ap = argparse.ArgumentParser(description="schema 迁移")
    ap.add_argument("--dry", action="store_true", help="只报告不落盘")
    a = ap.parse_args()
    rows = yaml.safe_load(io.open(DATA, encoding="utf-8").read()) or []
    rows, n = migrate(rows)
    print("条目 %d | 需补字段 %d 处%s" % (len(rows), n, "（dry-run，未落盘）" if a.dry else ""))
    if not a.dry and n:
        io.open(DATA, "w", encoding="utf-8").write(
            yaml.safe_dump(rows, allow_unicode=True, sort_keys=False))
        print("已写入", DATA)
    return 0

if __name__ == "__main__":
    sys.exit(main())
