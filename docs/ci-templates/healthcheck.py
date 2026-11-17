# -*- coding: utf-8 -*-
"""数据新鲜度与可用性探活脚本（模板）。

用途：供负责工程化与发布的成员接入定时任务。本文件是模板，
不会自动执行、不发送任何外部通知、不修改仓库数据。

检查项：
  1. 产出文件是否存在、能否解析
  2. 产出条数与源档案数是否一致
  3. status_as_of 是否过期（快照新鲜度）
  4. 数据校验脚本是否通过

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
DATA = ROOT / "data" / "conferences.yml"
SOURCE_DIR = ROOT / "conference"
VALIDATE = ROOT / "scripts" / "validate_data.py"


def check(name, ok, detail, issues):
    print("  [%s] %s: %s" % ("OK" if ok else "FAIL", name, detail))
    if not ok:
        issues.append("%s: %s" % (name, detail))


def main():
    ap = argparse.ArgumentParser(description="ACN 数据探活")
    ap.add_argument("--max-age-hours", type=int, default=48,
                    help="status_as_of 允许的最大滞后小时数")
    ap.add_argument("--json", default="", help="可选：输出 JSON 报告")
    args = ap.parse_args()

    issues = []
    print("=== ACN 数据探活 ===")

    # 1. 产出文件
    exists = DATA.is_file()
    check("产出文件", exists, str(DATA) if exists else "文件不存在", issues)
    rows = []
    if exists:
        try:
            rows = yaml.safe_load(io.open(DATA, encoding="utf-8").read()) or []
            check("产出解析", isinstance(rows, list), "%d 条" % len(rows), issues)
        except Exception as e:
            check("产出解析", False, str(e), issues)

    # 2. 条数一致性
    src_count = len([p for p in SOURCE_DIR.glob("**/*.yml") if p.name != "types.yml"])
    if isinstance(rows, list):
        check("条数一致", len(rows) == src_count,
              "产出 %d / 源档案 %d" % (len(rows), src_count), issues)

    # 3. 快照新鲜度
    if rows and isinstance(rows[0], dict):
        stamp = str(rows[0].get("status_as_of") or "")
        try:
            base = stamp.replace("+08:00", "")
            when = datetime.strptime(base, "%Y-%m-%dT%H:%M:%S")
            now = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=8)
            age = (now - when).total_seconds() / 3600.0
            check("状态快照新鲜度", age <= args.max_age_hours,
                  "距今 %.1f 小时（上限 %d）" % (age, args.max_age_hours), issues)
        except ValueError:
            check("状态快照新鲜度", False, "status_as_of 格式异常：%r" % stamp, issues)

    # 4. 数据校验脚本（只跑源档案，避免依赖生成物，探活更稳定）
    if VALIDATE.is_file():
        r = subprocess.run([sys.executable, str(VALIDATE), "--source"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        check("源档案校验", r.returncode == 0,
              "退出码 %d" % r.returncode, issues)
    else:
        check("源档案校验", False, "校验脚本不存在", issues)

    result = {"healthy": not issues, "issues": issues,
              "checked_at": datetime.now(timezone.utc).replace(tzinfo=None).isoformat() + "Z"}
    if args.json:
        Path(args.json).write_text(json.dumps(result, ensure_ascii=False, indent=2),
                                   encoding="utf-8")
        print("JSON 报告: %s" % args.json)
    print("结论: %s" % ("健康" if not issues else "存在 %d 项异常" % len(issues)))
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
