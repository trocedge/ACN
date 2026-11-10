# -*- coding: utf-8 -*-
"""CI 门禁红绿验证：改坏一份源档案 → 门禁必须阻断 → 原样恢复 → 门禁必须通过。

安全措施：字节级备份 + finally 恢复 + sha256 复核，任何异常都不会留下改动。
"""
import hashlib
import io
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT / "scripts" / "validate_data.py"
REPORT = ROOT / "docs" / "ci-red-green-report.md"
DATE_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}")


def gate():
    r = subprocess.run([sys.executable, str(GATE), "--source"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = (r.stdout or "") + (r.stderr or "")
    blocked = r.returncode != 0 and "ERROR（阻断） : 0" not in out
    return r.returncode, blocked, out


def find_target():
    """按行查找一处真实的 deadline 日期，不依赖空白字符正则。"""
    for path in sorted((ROOT / "conference").glob("**/*.yml")):
        if path.name == "types.yml":
            continue
        raw = path.read_bytes()
        text = raw.decode("utf-8", errors="replace")
        for line in text.splitlines(keepends=True):
            stripped = line.strip()
            if stripped.startswith("deadline:"):
                found = DATE_RE.search(stripped)
                if found:
                    return path, raw, text, line, found.group(0)
    return None


def main():
    found = find_target()
    if found is None:
        print("未找到可用于红绿验证的 deadline 字段")
        return 1
    target, raw, text, line, date = found
    digest = hashlib.sha256(raw).hexdigest()
    broken = text.replace(line, line.replace(date, "NOT-A-DATE", 1), 1)

    try:
        target.write_bytes(broken.encode("utf-8"))
        red_rc, red_blocked, red_out = gate()
    finally:
        target.write_bytes(raw)
    restored = hashlib.sha256(target.read_bytes()).hexdigest() == digest
    green_rc, green_blocked, green_out = gate()
    green_ok = green_rc == 0 and not green_blocked
    passed = red_blocked and green_ok and restored

    print("验证文件    : %s" % target.relative_to(ROOT).as_posix())
    print("红（非法日期）: 退出码 %s / 被阻断 %s" % (red_rc, red_blocked))
    print("绿（恢复后）  : 退出码 %s / 通过 %s" % (green_rc, green_ok))
    print("源文件恢复    : %s" % restored)
    print("结论          : %s" % ("通过" if passed else "未通过"))

    lines = ["# CI 门禁红绿验证记录", "",
             "> 由 `scripts/ci_red_green_check.py` 自动生成；改坏与恢复均在真实源档案上执行。",
             "- 执行时间：%s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             "- 验证文件：`%s`" % target.relative_to(ROOT).as_posix(), "",
             "| 阶段 | 操作 | 退出码 | 预期 | 结果 |", "|---|---|---:|---|---|",
             "| 红 | deadline 改为 NOT-A-DATE | %s | 非 0 且 ERROR 大于 0 | %s |" % (red_rc, "通过" if red_blocked else "未通过"),
             "| 恢复 | 字节级写回 + sha256 复核 | - | 与原文一致 | %s |" % ("通过" if restored else "未通过"),
             "| 绿 | 重新执行门禁 | %s | 0 且 ERROR 0 | %s |" % (green_rc, "通过" if green_ok else "未通过"), "",
             "结论：**%s**。" % ("通过，门禁具备阻断能力" if passed else "未通过，需排查校验规则"), "",
             "> 本脚本在 finally 中恢复原文件，异常退出也不会留下改动。", ""]
    io.open(REPORT, "w", encoding="utf-8").write(chr(10).join(lines))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
