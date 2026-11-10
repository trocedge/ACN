# -*- coding: utf-8 -*-
"""汇总校验报告趋势（只读归档，不改写历史）。"""
import io, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT / "docs" / "validation-archive"
OUT = ROOT / "docs" / "validation-trend.md"

def main():
    files = sorted(ARCHIVE.glob("*.json")) if ARCHIVE.is_dir() else []
    lines = ["# 校验趋势", "", "| 报告 | ERROR | WARN | 源档案 | 产出 |", "|---|---:|---:|---:|---:|"]
    for f in files:
        try:
            d = json.loads(io.open(f, encoding="utf-8").read())
            lines.append("| %s | %s | %s | %s | %s |" % (
                f.stem, d.get("errors", "?"), d.get("warnings", "?"),
                d.get("source_files", "?"), d.get("output_entries", "?")))
        except Exception:
            lines.append("| %s | 读取失败 | - | - | - |" % f.stem)
    if not files:
        lines.append("| 无数据 | - | - | - | - |")
    lines += ["", "> 归档目录为空表示尚无历史报告；缺数据不补 0。", ""]
    io.open(OUT, "w", encoding="utf-8").write("\n".join(lines))
    print("已生成", OUT, "| 报告数", len(files))
    return 0

if __name__ == "__main__":
    sys.exit(main())
