# -*- coding: utf-8 -*-
"""ACN 数据校验（可独立运行，供本地与 CI 使用）。

两种模式：
    python scripts/validate_data.py                 # 校验产出文件 data/conferences.yml
    python scripts/validate_data.py --source       # 校验源档案 conference/**/*.yml（PR 门禁）
    python scripts/validate_data.py --source --json report.json
                                                    # 输出机器可读报告

分级：
    ERROR  阻断性问题：结构错误、必填缺失、日期无法识别、id 重复、条数不一致
    WARN   提示性问题：时区写法不在推荐白名单、可选字段缺失、派生字段缺失、
                      录取率档案与会议标题未直接匹配

设计原则：只依据仓库中已有事实做判断，不推测、不补写、不修改任何文件。
"""
import argparse
import io
import json
import re
import sys
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "conference"
ACCEPT_DIR = ROOT / "accept_rates"
DEFAULT_OUT = ROOT / "data" / "conferences.yml"

REQUIRED_TOP = ("title", "description", "sub", "confs")
REQUIRED_EVENT = ("year", "id", "link", "timeline", "timezone")
SCHEMA_VERSION = "1.1"
VALID_STATUS = {"active", "past", "tbd", "unknown"}

# 推荐时区白名单：AoE / UTC / UTC±N / PT（PT 有夏令时，允许但标注）
TZ_RECOMMENDED = re.compile(r"^(AoE|UTC|UTC[+-]\d{1,2}|PT)$")
DEADLINE_SOURCE = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}|TBD)$")
DEADLINE_OUTPUT = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}|TBD)$")


class Report:
    def __init__(self):
        self.errors = []
        self.warns = []

    def err(self, msg):
        if len(self.errors) < 200:
            self.errors.append(msg)

    def warn(self, msg):
        if len(self.warns) < 200:
            self.warns.append(msg)

    def as_dict(self):
        return {
            "schema_version": SCHEMA_VERSION,
            "errors": len(self.errors),
            "warnings": len(self.warns),
            "error_samples": self.errors[:20],
            "warning_samples": self.warns[:20],
            "passed": not self.errors,
        }


def load_yaml(path):
    try:
        return yaml.safe_load(io.open(path, encoding="utf-8").read())
    except Exception as e:
        return {"__parse_error__": str(e)}


def validate_source(rep):
    """校验源档案：贡献者提交 PR 前跑这个，不依赖任何生成物。"""
    files = sorted(p for p in SRC_DIR.glob("**/*.yml") if p.name != "types.yml")
    rep.source_files = len(files)
    ids = []
    entry_count = 0

    for path in files:
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        data = load_yaml(path)
        if isinstance(data, dict) and "__parse_error__" in data:
            rep.err("%s 解析失败：%s" % (rel, data["__parse_error__"]))
            continue
        if not isinstance(data, list):
            rep.err("%s 顶层应为列表" % rel)
            continue
        for item in data:
            if not isinstance(item, dict):
                rep.err("%s 含非字典条目" % rel)
                continue
            entry_count += 1
            for key in REQUIRED_TOP:
                if key not in item:
                    rep.err("%s 缺必填字段 %s" % (rel, key))
            for conf in (item.get("confs") or []):
                if not isinstance(conf, dict):
                    rep.err("%s 届次不是字典" % rel)
                    continue
                for key in REQUIRED_EVENT:
                    if key not in conf:
                        rep.err("%s 届次缺必填字段 %s" % (rel, key))
                cid = conf.get("id")
                if cid:
                    ids.append(str(cid))
                tz = str(conf.get("timezone") or "").strip()
                if tz and not TZ_RECOMMENDED.match(tz):
                    rep.warn("%s 时区写法不在推荐白名单：%s" % (rel, tz))
                for key in ("date", "place"):
                    if key not in conf:
                        rep.warn("%s 届次缺可选字段 %s" % (rel, key))
                for point in (conf.get("timeline") or []):
                    if not isinstance(point, dict):
                        continue
                    dl = str(point.get("deadline") or "").strip()
                    if not DEADLINE_SOURCE.match(dl):
                        rep.err("%s 截止日格式不合规：%r" % (rel, dl))

    dup = [k for k, v in Counter(ids).items() if v > 1]
    if dup:
        rep.err("源档案存在重复 id %d 个：%s" % (len(dup), dup[:5]))
    rep.entries = entry_count
    rep.source_ids = len(ids)

    # 录取率档案与会议标题的关联检查：只提示，不阻断
    titles = set()
    for path in files:
        data = load_yaml(path)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get("title"):
                    titles.add(str(item["title"]).strip().lower())
    broken = []
    if ACCEPT_DIR.is_dir():
        for path in sorted(ACCEPT_DIR.glob("**/*.yml")):
            if path.stem.strip().lower() not in titles:
                broken.append(str(path.relative_to(ROOT)).replace("\\", "/"))
    rep.accept_files = len(list(ACCEPT_DIR.glob("**/*.yml"))) if ACCEPT_DIR.is_dir() else 0
    rep.accept_broken = broken
    if broken:
        rep.warn("录取率档案 %d 份未与会议标题直接匹配（建议建立 id 级关联）" % len(broken))


def validate_output(rep, path):
    """校验生成物：字段契约、日期、时区、状态、派生字段一致性。"""
    if not path.is_file():
        rep.err("产出文件不存在：%s" % path)
        return
    data = load_yaml(path)
    if isinstance(data, dict) and "__parse_error__" in data:
        rep.err("产出文件解析失败：%s" % data["__parse_error__"])
        return
    if not isinstance(data, list):
        rep.err("产出文件顶层应为列表")
        return
    rep.output_entries = len(data)
    ids = []
    for row in data:
        if not isinstance(row, dict):
            rep.err("产出含非字典条目")
            continue
        if row.get("schema_version") != SCHEMA_VERSION:
            rep.err("schema_version 不匹配：%r" % row.get("schema_version"))
        for key in ("title", "sub", "events"):
            if key not in row:
                rep.err("产出行缺字段 %s" % key)
        for ev in (row.get("events") or []):
            if not isinstance(ev, dict):
                continue
            if ev.get("id"):
                ids.append(str(ev["id"]))
            if ev.get("status") not in VALID_STATUS:
                rep.err("非法 status：%r" % ev.get("status"))
            off = ev.get("timezone_utc_offset")
            for point in (ev.get("timeline") or []):
                if not isinstance(point, dict):
                    continue
                dl = str(point.get("deadline") or "").strip()
                if not DEADLINE_OUTPUT.match(dl):
                    rep.err("产出截止日非 ISO 8601：%r" % dl)
                bj = point.get("deadline_beijing")
                # 无确定偏移却给出换算值 = 编造，必须阻断
                if off is None and bj:
                    rep.err("时区偏移未知却给出 deadline_beijing：%r" % bj)
    dup = [k for k, v in Counter(ids).items() if v > 1]
    if dup:
        rep.err("产出存在重复 id %d 个：%s" % (len(dup), dup[:5]))
    if getattr(rep, "source_files", None) and len(data) != rep.source_files:
        rep.err("产出条数 %d 与源档案数 %d 不一致" % (len(data), rep.source_files))


def main():
    ap = argparse.ArgumentParser(description="ACN 数据校验")
    ap.add_argument("--source", action="store_true", help="校验源档案（PR 门禁模式）")
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="产出文件路径")
    ap.add_argument("--json", default="", help="额外输出 JSON 报告路径")
    args = ap.parse_args()

    rep = Report()
    # 两种模式都先校验源档案，保证条数对照与必填检查始终生效
    validate_source(rep)
    if not args.source:
        validate_output(rep, Path(args.out))

    print("=== ACN 数据校验报告 ===")
    print("模式          : %s" % ("源档案（PR 门禁）" if args.source else "源档案 + 产出文件"))
    print("源档案文件    : %d" % getattr(rep, "source_files", 0))
    print("会议条目      : %d" % getattr(rep, "entries", 0))
    print("届次 id       : %d" % getattr(rep, "source_ids", 0))
    if not args.source:
        print("产出条目      : %d" % getattr(rep, "output_entries", 0))
    print("录取率档案    : %d 份，未直接匹配 %d 份" % (
        getattr(rep, "accept_files", 0), len(getattr(rep, "accept_broken", []))))
    print("ERROR（阻断） : %d" % len(rep.errors))
    print("WARN（提示）  : %d" % len(rep.warns))
    for e in rep.errors[:8]:
        print("  [ERROR] " + e)
    for w in rep.warns[:8]:
        print("  [WARN ] " + w)

    result = rep.as_dict()
    result["source_files"] = getattr(rep, "source_files", 0)
    result["entries"] = getattr(rep, "entries", 0)
    result["output_entries"] = getattr(rep, "output_entries", 0)
    result["accept_broken"] = len(getattr(rep, "accept_broken", []))
    if args.json:
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        io.open(args.json, "w", encoding="utf-8").write(
            json.dumps(result, ensure_ascii=False, indent=2))
        print("JSON 报告: %s" % args.json)
    print("结论          : %s" % ("通过" if not rep.errors else "未通过"))
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
