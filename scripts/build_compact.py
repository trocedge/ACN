# -*- coding: utf-8 -*-
"""ACN 数据格式改造原型（B 任务）。

设计原则（按学长 2026-11-09 群内要求）：
  1. 不照抄 oseddl 的 conferences/competitions/activities 三张表 —— 项目不需要「活动」等分类，
     只产出一份精简大表，行式展示友好。
  2. 保持原有数据链路：老 conference/**/*.yml 一个字不动，本脚本只读不写，
     别人继续按老格式提 PR，不受影响。
  3. 不删任何老字段：界面「仅保留重要内容」是展示层的事，数据层删字段不可逆，
     等 A 同学确认字段表后再精修。
  4. 时区只做「保留原值 + 补可确定的 UTC 偏移」，绝不把 AoE 硬替换成 Asia/Shanghai。

用法：
    python scripts/build_compact.py                  # 产出 data/conferences.yml
    python scripts/build_compact.py --out public/data/conferences.yml
    python scripts/build_compact.py --check          # 只校验不落盘
"""
import argparse
import io
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "conference"
DEFAULT_OUT = ROOT / "data" / "conferences.yml"

# 老仓库里的时区口径：AoE 定义即 UTC-12；PT 有夏令时，不固定，留空让前端按日期判
FIXED_OFFSET = {
    "AoE": -12, "UTC": 0, "UTC+0": 0, "AoE ": -12,
}
_UTC_RE = re.compile(r"^UTC([+-])(\d{1,2})$")
DATE_SPACE = re.compile(r"^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})$")
DATE_ONLY = re.compile(r"^\d{4}-\d{2}-\d{2}$")

REQUIRED = ("title", "description", "sub", "confs")


def utc_offset(tz):
    """能确定的才返回数字，不能确定（PT / 未知）返回 None，宁可留空也不错算。"""
    if not tz:
        return None
    tz = str(tz).strip()
    if tz in FIXED_OFFSET:
        return FIXED_OFFSET[tz]
    m = _UTC_RE.match(tz)
    if m:
        sign = 1 if m.group(1) == "+" else -1
        return sign * int(m.group(2))
    return None


def norm_deadline(value):
    """空格分隔 → ISO 8601 带 T；只有日期的按仓库约定补 23:59:59；TBD 原样保留。"""
    if value is None:
        return value, "empty"
    s = str(value).strip()
    if s == "TBD" or not s:
        return s, "tbd"
    m = DATE_SPACE.match(s)
    if m:
        return m.group(1) + "T" + m.group(2), "space_to_T"
    if DATE_ONLY.match(s):
        return s + "T23:59:59", "date_only_padded"
    if "T" in s:
        return s, "already_iso"
    return s, "unrecognized"


def load_entries():
    """扫描 712 份散 yml，返回 (会议列表, 统计计数器)。"""
    entries, stats = [], Counter()
    for path in sorted(SRC_DIR.glob("**/*.yml")):
        if path.name == "types.yml":
            continue
        stats["files"] += 1
        try:
            raw = io.open(path, encoding="utf-8").read()
            data = yaml.safe_load(raw)
        except Exception as e:
            stats["parse_error"] += 1
            print("  [解析失败] %s: %s" % (path.relative_to(ROOT), e), file=sys.stderr)
            continue
        if not isinstance(data, list):
            stats["not_list"] += 1
            continue
        for item in data:
            if not isinstance(item, dict):
                continue
            stats["conferences"] += 1
            entries.append((path, item))
    return entries, stats


def convert(entries, stats):
    """老结构 → 精简大表结构。字段一律保留，只做改名 / 日期规范化 / 时区补注。"""
    out = []
    for path, item in entries:
        # 老字段缺失检查（不阻塞，只记进报告）
        for key in REQUIRED:
            if key not in item:
                stats["missing_" + key] += 1

        events = []
        for conf in (item.get("confs") or []):
            if not isinstance(conf, dict):
                continue
            stats["editions"] += 1
            timeline = []
            for point in (conf.get("timeline") or []):
                if not isinstance(point, dict):
                    continue
                stats["timeline_points"] += 1
                new_point = dict(point)
                dl, how = norm_deadline(point.get("deadline"))
                new_point["deadline"] = dl
                stats["date_" + how] += 1
                timeline.append(new_point)

            tz = conf.get("timezone")
            off = utc_offset(tz)
            stats["tz_total"] += 1
            if off is None:
                stats["tz_unresolved"] += 1
            event = {
                "year": conf.get("year"),
                "id": conf.get("id"),
                "link": conf.get("link"),
                "timeline": timeline,
                "timezone": tz,                    # 原值，绝不硬替换
                "timezone_utc_offset": off,        # 能确定的补偏移，PT 等留 None
                "date": conf.get("date"),
                "place": conf.get("place"),
            }
            # 老数据里的扩展字段（abstract_deadline / link 变体 / 自定义键）一律带走
            for k, v in conf.items():
                if k not in event and k not in ("timeline", "timezone"):
                    event[k] = v
            events.append(event)

        row = {
            "title": item.get("title"),
            "description": item.get("description"),
            "sub": item.get("sub"),                # 学科，行式列表筛选要用
            "rank": item.get("rank"),             # CCF 评级，项目内核，保留
            "dblp": item.get("dblp"),             # 保留，等 A 确认是否展示
            "source_file": str(path.relative_to(ROOT)).replace("\\", "/"),
            "events": events,                    # confs → events
        }
        for k, v in item.items():
            if k not in row and k != "confs":
                row[k] = v
        out.append(row)
    return out


def validate(rows, stats):
    """返回问题列表；空列表表示校验通过。"""
    problems = []
    ids = [e.get("id") for r in rows for e in r["events"]]
    dup = [k for k, v in Counter(i for i in ids if i).items() if v > 1]
    if dup:
        problems.append("重复 id %d 个：%s" % (len(dup), dup[:5]))
    if not rows:
        problems.append("产出为空")
    if stats.get("parse_error"):
        problems.append("%d 个文件解析失败" % stats["parse_error"])
    if stats.get("date_unrecognized"):
        problems.append("%d 条日期格式无法识别，需人工看" % stats["date_unrecognized"])
    for r in rows:
        if not r.get("title"):
            problems.append("有条目缺 title：%s" % r.get("source_file"))
            break
    return problems


def main():
    ap = argparse.ArgumentParser(description="ACN 数据格式改造（B 任务）")
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="输出路径")
    ap.add_argument("--check", action="store_true", help="只校验不落盘")
    args = ap.parse_args()

    entries, stats = load_entries()
    rows = convert(entries, stats)
    problems = validate(rows, stats)

    print("=== ACN 数据格式改造报告 ===")
    print("扫描文件      : %d" % stats["files"])
    print("会议条目      : %d" % stats["conferences"])
    print("届次 events   : %d" % stats["editions"])
    print("timeline 节点 : %d" % stats["timeline_points"])
    print("日期规范化    : 空格转T %d / 补时刻 %d / 已ISO %d / TBD %d / 未识别 %d" % (
        stats["date_space_to_T"], stats["date_date_only_padded"],
        stats["date_already_iso"], stats["date_tbd"], stats["date_unrecognized"]))
    print("时区          : 共 %d 条，其中无法固定换算 %d 条（PT 等，保留原值）" % (
        stats["tz_total"], stats["tz_unresolved"]))
    print("AoE 原值保留  : 是（UTC-12，绝不替换成 Asia/Shanghai）")
    print("校验问题      : %s" % (problems if problems else "无"))

    if args.check:
        print("\n[校验模式] 未写文件。")
        return 1 if problems else 0

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with io.open(out, "w", encoding="utf-8") as f:
        yaml.safe_dump(rows, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
    print("\n已产出: %s (%.1f KB)" % (out, out.stat().st_size / 1024.0))
    # 老链路完整性：只做只读确认，不改 build_data.py / 不删任何 yml
    print("老文件未改动 : %s" % (SRC_DIR.exists() and "conference/ 仍在"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
