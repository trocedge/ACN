# -*- coding: utf-8 -*-
"""按当前时刻重算产出文件里的 status / status_basis / sort_key / status_as_of。

用于解决「状态是生成时刻快照、长期会过期」的问题；结构幂等（字段集合不变），
时间戳按执行时刻更新。支持 --dry 只报告不落盘，便于 CI 定时演练。
"""
import argparse
import io
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import yaml
from build_compact_data import compute_status, make_sort_key

DATA = ROOT / "data" / "conferences.yml"


def refresh(rows, now):
    changed = 0
    stamp = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    naive = now.replace(tzinfo=None)
    for r in rows:
        if r.get("status_as_of") != stamp:
            r["status_as_of"] = stamp
            changed += 1
        for e in r.get("events") or []:
            timeline = e.get("timeline") or []
            result = compute_status(timeline, naive)
            if isinstance(result, tuple) and len(result) == 2:
                status, basis = result
            else:
                status, basis = result, e.get("status_basis")
            for key, value in (("status", status), ("status_basis", basis),
                               ("sort_key", make_sort_key(status, timeline))):
                if e.get(key) != value:
                    e[key] = value
                    changed += 1
        all_points = [p for e in r.get("events") or [] for p in (e.get("timeline") or [])]
        best = min((e.get("status") for e in r.get("events") or []),
                   key=lambda x: {"active": 0, "tbd": 1, "past": 2, "unknown": 3}.get(x, 3),
                   default="unknown")
        key = make_sort_key(best, all_points)
        if r.get("sort_key") != key:
            r["sort_key"] = key
            changed += 1
    return changed


def main():
    ap = argparse.ArgumentParser(description="状态快照重算")
    ap.add_argument("--dry", action="store_true", help="只报告不落盘")
    args = ap.parse_args()
    rows = yaml.safe_load(io.open(DATA, encoding="utf-8").read()) or []
    now = datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0)
    changed = refresh(rows, now)
    print("条目 %d | 变化字段 %d 处 | 状态时刻 %s%s" % (
        len(rows), changed, now.isoformat(), "（dry-run，未落盘）" if args.dry else ""))
    if not args.dry and changed:
        io.open(DATA, "w", encoding="utf-8").write(
            yaml.safe_dump(rows, allow_unicode=True, sort_keys=False))
        print("已写入", DATA)
    return 0


if __name__ == "__main__":
    sys.exit(main())
