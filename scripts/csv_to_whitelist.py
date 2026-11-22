#!/usr/bin/env python3
"""CSV 批量录入竞赛白名单。

把填好的 CSV 表格合并进 competition/whitelist.yml，免去手敲 YAML。

用法：
    python scripts/csv_to_whitelist.py competition/import-template.csv
    python scripts/csv_to_whitelist.py 我的名单.csv

表头固定：seq,title,sub,category,site,deadline,timezone,source_url

规则：
- seq 命中已有条目 -> 只更新 CSV 中非空的字段（空单元格 = 不改动）
- seq 是全新序号 -> 追加到末尾（必须含 title/sub/category 等必填字段）
- deadline 为空 -> 整组省略 deadline/timezone/source_url
- 校验复用 validate_competition.validate_items，报错定位到 CSV 行号
- 写回前自动备份 whitelist.yml 为 .bak
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from validate_competition import validate_items  # noqa: E402

DEFAULT_WHITELIST = ROOT / "competition" / "whitelist.yml"
DEFAULT_TYPES = ROOT / "competition" / "types.yml"

HEADER = ["seq", "title", "sub", "category", "site", "deadline", "timezone", "source_url"]

# 写回 YAML 时的字段顺序
FIELD_ORDER = ["seq", "title", "sub", "category", "site", "deadline", "timezone", "source_url"]

# 需要单引号包裹的字段（title 可能含特殊字符，deadline 含冒号）
QUOTE_FIELDS = {"title", "deadline"}


def read_header_block(path: Path) -> str:
    """提取 whitelist.yml 的头部注释（第一条 - seq 之前的所有行）。"""
    collected: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("- "):
            break
        collected.append(line)
    return "\n".join(collected) + "\n"


def _quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def serialize_items(items: list[dict]) -> str:
    """按现有 whitelist.yml 的排版把条目序列化为 YAML。"""
    lines: list[str] = []
    for item in items:
        lines.append(f"- seq: {item['seq']}")
        for key in FIELD_ORDER[1:]:
            if key not in item or item[key] is None or item[key] == "":
                continue
            value = str(item[key])
            if key in QUOTE_FIELDS:
                value = _quote(value)
            lines.append(f"  {key}: {value}")
    return "\n".join(lines) + "\n"


def parse_csv_rows(csv_path: Path) -> tuple[list[tuple[int, dict]], list[str]]:
    """读 CSV，返回 [(行号, 清理后的字段 dict), ...] 与错误列表。

    空单元格直接省略；整行空的跳过；seq 保留字符串，合并阶段再转 int。
    """
    rows: list[tuple[int, dict]] = []
    errors: list[str] = []
    try:
        with open(csv_path, encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                return rows, [f"{csv_path.name} 是空文件或缺少表头"]
            missing = [h for h in HEADER if h not in reader.fieldnames]
            extra = [h for h in reader.fieldnames if h not in HEADER]
            if missing:
                errors.append(f"表头缺少字段: {missing}")
            if extra:
                errors.append(f"表头含未知字段: {extra}")
            if missing or extra:
                return rows, errors
            for row_number, raw in enumerate(reader, start=2):
                item = {k: (v or "").strip() for k, v in raw.items()}
                item = {k: v for k, v in item.items() if v != ""}
                if not item:
                    continue
                rows.append((row_number, item))
    except OSError as exc:
        return rows, [f"读 CSV 失败: {exc}"]
    return rows, errors


def merge_and_validate(existing: list[dict], types: list[dict],
                       rows: list[tuple[int, dict]]) -> tuple[list[dict], list[int], list[int], list[str]]:
    """合并 CSV 行到现有条目，逐行校验并返回 (合并后列表, 新增 seq, 更新 seq, 错误)。"""
    existing_by_seq = {item["seq"]: item for item in existing}
    merged = [dict(item) for item in existing]
    added: list[int] = []
    updated: list[int] = []
    seen_in_csv: set[int] = set()
    errors: list[str] = []

    for row_number, item in rows:
        seq_raw = item.get("seq")
        try:
            seq = int(seq_raw)
        except (TypeError, ValueError):
            errors.append(f"CSV 第 {row_number} 行: seq={seq_raw!r} 不是整数")
            continue
        if seq in seen_in_csv:
            errors.append(f"CSV 第 {row_number} 行: seq={seq} 与本 CSV 前面的行重复")
            continue
        seen_in_csv.add(seq)

        rest = {k: v for k, v in item.items() if k != "seq"}
        if seq in existing_by_seq:
            candidate = dict(existing_by_seq[seq])
            candidate.update(rest)
        else:
            candidate = {"seq": seq, **rest}

        single_errors = validate_items([candidate], types, strict_count=False)
        if single_errors:
            errors.append(f"CSV 第 {row_number} 行(seq={seq}): {'; '.join(single_errors)}")
            continue

        if seq in existing_by_seq:
            for i, entry in enumerate(merged):
                if entry.get("seq") == seq:
                    merged[i] = candidate
                    break
            updated.append(seq)
        else:
            merged.append(candidate)
            existing_by_seq[seq] = candidate
            added.append(seq)

    # 合并后整体兜底校验（基础 1—84 连续 + 85 起连续扩展）
    if not errors:
        full_errors = validate_items(merged, types, strict_count=True)
        if full_errors:
            errors.extend(full_errors)

    return merged, added, updated, errors


def main() -> None:
    parser = argparse.ArgumentParser(description="CSV 批量录入竞赛白名单")
    parser.add_argument("csv", type=Path, help="CSV 文件路径（表头见 import-template.csv）")
    parser.add_argument("--whitelist", type=Path, default=DEFAULT_WHITELIST)
    parser.add_argument("--types", type=Path, default=DEFAULT_TYPES)
    args = parser.parse_args()

    if not args.csv.exists():
        print(f"错误: 找不到 CSV 文件 {args.csv}")
        sys.exit(1)

    header = read_header_block(args.whitelist)
    existing = yaml.safe_load(args.whitelist.read_text(encoding="utf-8")) or []
    types = yaml.safe_load(args.types.read_text(encoding="utf-8")) or []

    rows, read_errors = parse_csv_rows(args.csv)
    if read_errors:
        print(f"读取 CSV 失败，共 {len(read_errors)} 处：")
        for e in read_errors:
            print(f"  - {e}")
        sys.exit(1)

    merged, added, updated, errors = merge_and_validate(existing, types, rows)
    if errors:
        print(f"校验失败，共 {len(errors)} 处，未写入 {args.whitelist.name}：")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    backup = args.whitelist.with_name(args.whitelist.name + ".bak")
    backup.write_text(args.whitelist.read_text(encoding="utf-8"), encoding="utf-8")

    out = header + serialize_items(merged)
    args.whitelist.write_text(out, encoding="utf-8")

    print(f"写入成功: {args.whitelist}")
    print(f"  新增 {len(added)} 项: {added}")
    print(f"  更新 {len(updated)} 项: {updated}")
    print(f"  现有 {len(existing)} 项 -> 合并后 {len(merged)} 项")
    print(f"  已备份原文件到: {backup.name}")


if __name__ == "__main__":
    main()
