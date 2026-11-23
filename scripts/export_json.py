import json
import os
from pathlib import Path

import yaml


# 脚本自己的位置是 <仓库>/scripts/export_json.py，
# 往上退一级就是仓库根
ROOT = Path(__file__).resolve().parent.parent

YAML_PATH = Path(os.environ.get("COMPETITION_YAML") or ROOT / "competition" / "whitelist.yml")
OUT_PATH = Path(os.environ.get("COMPETITION_JSON") or ROOT / "public" / "competition" / "whitelist.json")

# captured_at 记录的是「这份名单哪次采集的」，不是构建时间；用环境变量覆盖。
CAPTURED_AT = os.environ.get("COMPETITION_CAPTURED_AT", "2026-11-17")

SOURCE = "中国高等教育学会《2024全国普通高校大学生竞赛分析报告》竞赛目录"
SOURCE_URL = "https://sk.njts.edu.cn/2024/0913/c3721a84943/page.htm"
NOTE = "竞赛名称与分类为官方目录核实数据；deadline/source_url 为可选字段，未核实则不出现"

# 与 src/components/competition.rs 的 CompetitionItem 对齐；
# 可选字段未核实就不输出，前端按「未核实则不存在」处理。
OPTIONAL_FIELDS = ("site", "deadline", "timezone", "source_url")


def load_items(path):
    """读 yml，只输出前端结构体认识的字段，空值不落盘。"""
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or []
    items = []
    for it in raw:
        item = {
            "seq": it["seq"],
            "title": it.get("title", ""),
            "sub": it.get("sub", ""),
            "category": it.get("category", ""),
        }
        for key in OPTIONAL_FIELDS:
            if it.get(key):
                item[key] = it[key]
        items.append(item)
    return items


def main():
    items = load_items(YAML_PATH)

    payload = {
        "source": SOURCE,
        "source_url": SOURCE_URL,
        "captured_at": CAPTURED_AT,
        "total": len(items),
        "note": NOTE,
        "items": items,
    }

    out = Path(OUT_PATH)
    out.parent.mkdir(parents=True, exist_ok=True)  # 目录不存在就建
    out.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(f"已导出 {len(items)} 条 -> {out}")


if __name__ == "__main__":
    main()
