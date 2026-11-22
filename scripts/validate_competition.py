#!/usr/bin/env python3
"""竞赛白名单数据校验。

供本地与 CI 共用，在 build_data.py 之前运行。
用法：
    python scripts/validate_competition.py                     # 校验正式数据 + 产物一致性
    python scripts/validate_competition.py --whitelist A.yml --types B.yml
                                                               # 只校验指定文件（测试夹具用）

校验规则见 docs/page-inventory.md 与 competition/whitelist.yml 头部说明。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_WHITELIST = ROOT / "competition" / "whitelist.yml"
DEFAULT_TYPES = ROOT / "competition" / "types.yml"
DEFAULT_JSON = ROOT / "public" / "competition" / "whitelist.json"

# 官方目录基础项 84 个，序号 1—84 必须连续；85 起允许向后连续扩展
OFFICIAL_COUNT = 84

# ISO 8601 日期时间，例：2027-03-15T18:00:00
DEADLINE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")

ALLOWED_FIELDS = {"seq", "title", "sub", "category", "site",
                  "deadline", "timezone", "source_url"}


def load_yaml(path: Path):
    if not path.exists():
        print(f"错误: 找不到文件 {path}")
        sys.exit(1)
    return yaml.safe_load(path.read_text(encoding="utf-8")) or []


def validate_items(items, types, *, strict_count: bool = True) -> list[str]:
    """返回错误信息列表，空列表表示通过。strict_count=False 时跳过 84 项连续性检查（夹具用）。"""
    errors = []
    known_subs = {t["sub"] for t in types if isinstance(t, dict) and "sub" in t}
    seen_seq = {}
    seen_title = {}

    for i, item in enumerate(items):
        where = f"第 {i + 1} 条(seq={item.get('seq', '?')})"

        if not isinstance(item, dict):
            errors.append(f"{where}: 不是映射结构")
            continue

        unknown = set(item) - ALLOWED_FIELDS
        if unknown:
            errors.append(f"{where}: 含未知字段 {sorted(unknown)}")

        seq = item.get("seq")
        if not isinstance(seq, int) or isinstance(seq, bool):
            errors.append(f"{where}: seq 必须是整数")
        elif seq in seen_seq:
            errors.append(f"{where}: seq={seq} 与第 {seen_seq[seq]} 条重复")
        else:
            seen_seq[seq] = i + 1

        title = item.get("title")
        if not title or not str(title).strip():
            errors.append(f"{where}: title 不能为空")
        elif title in seen_title:
            errors.append(f"{where}: title 与第 {seen_title[title]} 条重复")
        else:
            seen_title[title] = i + 1

        if item.get("sub") not in known_subs:
            errors.append(f"{where}: sub={item.get('sub')!r} 不在 types.yml 中")

        site = item.get("site")
        if site is not None:
            if not isinstance(site, str) or not site.strip():
                errors.append(f"{where}: site 为空时应直接省略该字段")
            elif not re.match(r"^https?://\S+$", site):
                errors.append(f"{where}: site={site!r} 不是合法 http/https 链接")

        deadline = item.get("deadline")
        source_url = item.get("source_url")
        if deadline is not None:
            if not isinstance(deadline, str) or not DEADLINE_RE.match(deadline):
                errors.append(f"{where}: deadline={deadline!r} 不是 ISO 8601 时间(YYYY-MM-DDTHH:mm:ss)")
            else:
                try:
                    datetime.strptime(deadline, "%Y-%m-%dT%H:%M:%S")
                except ValueError:
                    errors.append(f"{where}: deadline={deadline!r} 日期不存在")
            if not source_url:
                errors.append(f"{where}: 填了 deadline 必须同时填 source_url 标注来源")
            elif not re.match(r"^https?://\S+$", source_url):
                errors.append(f"{where}: source_url={source_url!r} 不是合法链接")
            tz = item.get("timezone", "Asia/Shanghai")
            if tz != "Asia/Shanghai":
                errors.append(f"{where}: timezone 只支持 Asia/Shanghai，当前为 {tz!r}")
        elif source_url:
            errors.append(f"{where}: 只有 deadline 才需要 source_url")

    if strict_count:
        seqs = sorted(seen_seq)
        if items:
            base = list(range(1, OFFICIAL_COUNT + 1))
            base_seqs = [s for s in seqs if s <= OFFICIAL_COUNT]
            extra_seqs = [s for s in seqs if s > OFFICIAL_COUNT]
            missing = sorted(set(base) - set(base_seqs))
            extra_expected = list(range(OFFICIAL_COUNT + 1, OFFICIAL_COUNT + 1 + len(extra_seqs)))
            extra_broken = extra_seqs != extra_expected
            if missing or extra_broken:
                detail = []
                if missing:
                    detail.append(f"缺 {missing}")
                if extra_broken:
                    detail.append(f"扩展项应为 {OFFICIAL_COUNT + 1} 起连续，当前 {extra_seqs}")
                errors.append(f"正式白名单应为 1—{OFFICIAL_COUNT} 连续序号（85 起可向后连续扩展）: {'; '.join(detail)}")

    return errors


def validate_output(items, json_path: Path) -> list[str]:
    """校验构建产物与源数据一致。"""
    if not json_path.exists():
        return [f"产物 {json_path} 不存在，请先运行 build_data.py"]
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return [f"产物 {json_path} 读取失败: {exc}"]

    out_items = data.get("items", [])
    if len(out_items) != len(items):
        return [f"产物条数 {len(out_items)} 与源 {len(items)} 不一致"]
    for src, out in zip(items, out_items):
        if src.get("seq") != out.get("seq"):
            return [f"产物 seq 顺序与源不一致: 源 {src.get('seq')} vs 产物 {out.get('seq')}"]
    return []


def main() -> None:
    parser = argparse.ArgumentParser(description="竞赛白名单数据校验")
    parser.add_argument("--whitelist", type=Path, default=DEFAULT_WHITELIST)
    parser.add_argument("--types", type=Path, default=DEFAULT_TYPES)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON,
                        help="构建产物路径，与默认不同则跳过产物一致性检查")
    args = parser.parse_args()

    items = load_yaml(args.whitelist)
    types = load_yaml(args.types)

    strict = args.whitelist.resolve() == DEFAULT_WHITELIST.resolve()
    errors = validate_items(items, types, strict_count=strict)
    if strict and not errors:
        errors += validate_output(items, args.json)

    if errors:
        print(f"竞赛数据校验失败，共 {len(errors)} 处：")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    print(f"竞赛数据校验通过: {args.whitelist.name} 共 {len(items)} 项"
          + ("（含产物一致性）" if strict else ""))


if __name__ == "__main__":
    main()
