# -*- coding: utf-8 -*-
"""列出 TBD 条目的建议复查清单。只读，不修改任何数据。"""
import io, sys, yaml
from datetime import datetime
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "conferences.yml"

def main():
    if not DATA.is_file():
        print("产出文件不存在，请先运行 build_compact_data.py"); return 1
    rows = yaml.safe_load(io.open(DATA, encoding="utf-8").read()) or []
    out = []
    for r in rows:
        for e in r.get("events") or []:
            for p in e.get("timeline") or []:
                if p.get("deadline") == "TBD":
                    out.append((p.get("tbd_review") or "", r.get("title"),
                                e.get("id"), p.get("tbd_source") or "", p.get("tbd_owner") or ""))
    out.sort()
    print("TBD 待复查条目：%d 条" % len(out))
    for review, title, eid, src, owner in out[:20]:
        print("  %s | %s | %s | %s | %s" % (review, title, eid, src, owner))
    if len(out) > 20:
        print("  ... 其余 %d 条省略" % (len(out) - 20))
    return 0

if __name__ == "__main__":
    sys.exit(main())
