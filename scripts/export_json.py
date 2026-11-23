import json
import os
from datetime import date
from pathlib import Path

import yaml
import os
from pathlib import Path


# 脚本自己的位置是 <仓库>/scripts/export_json.py，
# 往上退一级就是仓库根
ROOT = Path(__file__).resolve().parent.parent

YAML_PATH = Path(os.environ.get("COMPETITION_YAML") or ROOT / "competition" / "whitelist.yml")
OUT_PATH = Path(os.environ.get("COMPETITION_JSON") or ROOT / "public" / "competition" / "whitelist.json")



def load_items(path):
    """读 yml，把每条整理成统一的 dict，空值补成 "" 或 None。"""
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or []
    items = []
    for it in raw:
        items.append({
            "seq": it.get("seq"),
            "title": it.get("title", ""),
            "sub": it.get("sub", ""),
            "category": it.get("category", ""),
            "site": it.get("site") or "",          # 没官网就给空字符串，不给缺键
            "season": it.get("season"),           # 预留字段，现在是 None
            "deadline": it.get("deadline"),
            "deadline_source": it.get("deadline_source"),
        })
    return items


def main():
    items = load_items(YAML_PATH)

    payload = {
        "source": "中国高等教育学会《2024全国普通高校大学生竞赛分析报告》竞赛目录",
        "source_url": "https://sk.njts.edu.cn/2024/0913/c3721a84943/page.htm",
        "captured_at": date.today().isoformat(),   # 生成日期
        "total": len(items),
        "note": "仅含竞赛名称与分类，报名截止时间待采集",
        "items": items,
    }

    out = Path(OUT_PATH)
    out.parent.mkdir(parents=True, exist_ok=True)  # 目录不存在就建
    out.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"已导出 {len(items)} 条 -> {out}")


if __name__ == "__main__":
    main()
