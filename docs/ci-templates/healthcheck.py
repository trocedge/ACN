# -*- coding: utf-8 -*-
"""数据新鲜度与可用性探活脚本（模板）。

用途：供负责工程化与发布的成员接入定时任务。本文件是模板，
不会自动执行、不发送任何外部通知、不修改仓库数据。

站点在 2026-11 改为竞赛资讯首页，会议数据退出部署产物，因此探活以
竞赛目录产物为主线，会议快照只做提示、不再阻断。

阻断项（退出码非 0）：
  1. public/competition/whitelist.json 是否存在、能否解析
  2. 声明的 total 与实际条目数是否一致
  3. 产物条数与源档案 competition/whitelist.yml 是否一致（防止改了源忘记重新生成）
  4. 每条竞赛的 sub 是否都能在 public/competition/types.json 中找到

提示项（只报告，不影响退出码）：
  5. 会议快照 data/conferences.yml 的 status_as_of 新鲜度
  6. 会议源档案校验（scripts/validate_data.py --source）

用法：
    python docs/ci-templates/healthcheck.py
    python docs/ci-templates/healthcheck.py --max-age-hours 48 --json health.json

退出码：0=健康，1=异常，便于 CI / 定时任务判断。
"""
import argparse
import io
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
COMP_PRODUCT_DIR = ROOT / "public" / "competition"
WHITELIST_JSON = COMP_PRODUCT_DIR / "whitelist.json"
TYPES_JSON = COMP_PRODUCT_DIR / "types.json"
WHITELIST_SRC = ROOT / "competition" / "whitelist.yml"

# 会议数据已退出部署产物，下面两项只作提示。
DATA = ROOT / "data" / "conferences.yml"
# 会议档案在 2026-11 由 conference/ 迁入 archive/conference/，两种结构都要能探活。
SOURCE_DIR = next(
    (ROOT / candidate for candidate in ("archive/conference", "conference")
     if (ROOT / candidate).is_dir()),
    ROOT / "archive" / "conference",
)
VALIDATE = ROOT / "scripts" / "validate_data.py"


def check(name, ok, detail, issues, warnings, warn=False):
    level = "OK" if ok else ("WARN" if warn else "FAIL")
    print("  [%s] %s: %s" % (level, name, detail))
    if not ok:
        (warnings if warn else issues).append("%s: %s" % (name, detail))


def load_json(path, name, issues, warnings):
    if not path.is_file():
        check(name, False, "文件不存在：%s" % path.relative_to(ROOT), issues, warnings)
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - 解析失败即探活失败
        check(name, False, str(exc), issues, warnings)
        return None
    check(name, True, "%s" % path.relative_to(ROOT), issues, warnings)
    return data


def main():
    ap = argparse.ArgumentParser(description="ACN 数据探活")
    ap.add_argument("--max-age-hours", type=int, default=48,
                    help="会议快照 status_as_of 允许的最大滞后小时数（提示项）")
    ap.add_argument("--json", default="", help="可选：输出 JSON 报告")
    args = ap.parse_args()

    issues, warnings = [], []
    print("=== ACN 数据探活（竞赛目录主线） ===")

    # 1. 竞赛目录产物
    whitelist = load_json(WHITELIST_JSON, "竞赛目录产物", issues, warnings)
    types = load_json(TYPES_JSON, "竞赛分类产物", issues, warnings)

    items = []
    if isinstance(whitelist, dict):
        items = whitelist.get("items") or []
        if not isinstance(items, list) or not items:
            check("竞赛目录内容", False, "items 为空或格式异常", issues, warnings)
            items = []
        else:
            check("竞赛目录内容", True, "%d 条" % len(items), issues, warnings)
            declared = whitelist.get("total")
            check("总数一致", declared == len(items),
                  "声明 %s / 实际 %d" % (declared, len(items)), issues, warnings)

    # 2. 产物与源档案条数一致
    if WHITELIST_SRC.is_file():
        try:
            source_rows = yaml.safe_load(io.open(WHITELIST_SRC, encoding="utf-8").read()) or []
            check("产物同步源档案", len(source_rows) == len(items),
                  "产物 %d / 源 %d" % (len(items), len(source_rows)), issues, warnings)
        except Exception as exc:  # noqa: BLE001
            check("产物同步源档案", False, str(exc), issues, warnings)
    else:
        check("产物同步源档案", False,
              "源档案不存在：%s" % WHITELIST_SRC.relative_to(ROOT), issues, warnings)

    # 3. 分类不能悬空
    if isinstance(types, list) and items:
        known = {str(t.get("sub")) for t in types if isinstance(t, dict)}
        dangling = sorted({str(i.get("sub")) for i in items} - known)
        check("分类覆盖", not dangling,
              "未知分类 %s" % ", ".join(dangling) if dangling else "%d 个分类全部命中" % len(known),
              issues, warnings)

    # 4. 会议快照新鲜度（提示）
    if DATA.is_file():
        try:
            rows = yaml.safe_load(io.open(DATA, encoding="utf-8").read()) or []
            stamp = str((rows[0] or {}).get("status_as_of") or "") if rows else ""
            base = stamp.replace("+08:00", "")
            when = datetime.strptime(base, "%Y-%m-%dT%H:%M:%S")
            now = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=8)
            age = (now - when).total_seconds() / 3600.0
            check("会议快照新鲜度", age <= args.max_age_hours,
                  "距今 %.1f 小时（上限 %d，会议数据已不随部署更新）"
                  % (age, args.max_age_hours), issues, warnings, warn=True)
        except Exception as exc:  # noqa: BLE001
            check("会议快照新鲜度", False, str(exc), issues, warnings, warn=True)

    # 5. 会议源档案校验（提示）
    if VALIDATE.is_file():
        r = subprocess.run([sys.executable, str(VALIDATE), "--source"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        check("会议源档案校验", r.returncode == 0,
              "退出码 %d" % r.returncode, issues, warnings, warn=True)
    else:
        check("会议源档案校验", False, "校验脚本不存在", issues, warnings, warn=True)

    result = {"healthy": not issues, "issues": issues, "warnings": warnings,
              "checked_at": datetime.now(timezone.utc).replace(tzinfo=None).isoformat() + "Z"}
    if args.json:
        Path(args.json).write_text(json.dumps(result, ensure_ascii=False, indent=2),
                                   encoding="utf-8")
        print("JSON 报告: %s" % args.json)
    tail = "健康" if not issues else "存在 %d 项异常" % len(issues)
    if warnings:
        tail += "（另有 %d 项提示）" % len(warnings)
    print("结论: %s" % tail)
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
