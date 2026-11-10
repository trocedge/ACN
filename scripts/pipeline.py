# -*- coding: utf-8 -*-
"""全链路一键执行：源档案校验 → 老链路 → 新表 → 完整校验 → 探活 → 新增单测。

解决「改一份 yml 要手动跑两个脚本」的问题；任一步失败即退出非零。
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STEPS = [
    ("源档案门禁", [sys.executable, "scripts/validate_data.py", "--source"]),
    ("老链路生成", [sys.executable, "scripts/build_data.py"]),
    ("新表生成", [sys.executable, "scripts/build_compact_data.py"]),
    ("完整校验", [sys.executable, "scripts/validate_data.py"]),
    ("数据探活", [sys.executable, "docs/ci-templates/healthcheck.py"]),
    ("新增单测", [sys.executable, "-m", "unittest", "scripts.test_schema_compat",
                "scripts.test_validation_rules", "scripts.test_deadline_compat"]),
]


def main():
    failed = []
    for name, cmd in STEPS:
        r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True,
                           text=True, encoding="utf-8", errors="replace")
        ok = r.returncode == 0
        print("[%s] %s (exit=%d)" % ("OK" if ok else "FAIL", name, r.returncode))
        if not ok:
            failed.append(name)
            print((r.stdout or "")[-600:] + (r.stderr or "")[-400:])
    print("流水线：%d/%d 步通过" % (len(STEPS) - len(failed), len(STEPS)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
