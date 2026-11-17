# -*- coding: utf-8 -*-
"""扫描文档里可能过期的硬编码数字，输出核查清单；不改写任何文档。"""
import io
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs"
OUT = DOC / "doc-stats-check.md"
STALE = ["1912/2357", "2105/2357", "1724/2357", "445 条", "23 份断链",
         "82 项 / 14", "14 项既有错误", "约 61", "61 分", "12 项错误"]

def main():
    hits = []
    for path in sorted(DOC.glob("*.md")):
        if path.name in ("doc-stats-check.md", "corrections.md"):
            continue
        text = io.open(path, encoding="utf-8").read()
        for token in STALE:
            if token in text:
                hits.append((path.name, token))
    lines = ["# 文档数字一致性核查", "",
             "> 由 `scripts/check_doc_stats.py` 生成。命中项为历史数字，",
             "> 多数文档已带更正指引；本清单用于变更后逐条复核，不自动改写。", "",
             "| 文件 | 命中的历史数字 |", "|---|---|"]
    for name, token in hits:
        lines.append("| `%s` | %s |" % (name, token))
    if not hits:
        lines.append("| 无 | - |")
    lines += ["", "共 %d 处。实时数字以 `docs/stats.md` 与门禁输出为准。" % len(hits), ""]
    io.open(OUT, "w", encoding="utf-8").write("\n".join(lines))
    print("命中 %d 处，已写入 %s" % (len(hits), OUT))
    return 0

if __name__ == "__main__":
    main()
