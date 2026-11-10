# CI 门禁启用说明（第 21 条）
仓库既有 `merge_check.yml` 已运行 `scripts/validate.py`（schema 校验）与 `build_data.py`，
本次新增 `data-check.yml` 用于覆盖**新数据格式与新脚本**，两者并存不冲突。
## 红/绿验证步骤
1. 临时把某份 `conference/*.yml` 的 `deadline` 改成非法格式 → 提 PR → 应被 `data-check` 阻断。
2. 恢复原值 → 重新运行 → 应通过。
3. 记录两次运行结果与耗时。
## 边界
未改动任何既有 workflow；新增文件推送后自动生效。

## 红绿验证已执行（2026-11-10，本地真实执行）

`scripts/ci_red_green_check.py` 在真实源档案上临时把一处 `deadline` 改为 `NOT-A-DATE`：
门禁退出码非 0 且 ERROR>0（红）→ `finally` 字节级恢复并 sha256 复核 → 重新执行门禁退出码 0（绿）。
结果见 `docs/ci-red-green-report.md`。推送后 CI 将自动具备同等阻断能力。
