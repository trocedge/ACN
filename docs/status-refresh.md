# 状态快照重算说明（D2）

## 问题
`status`（active / past / tbd）与 `status_as_of` 是 `build_compact_data.py` 生成时刻的快照，长期会过期。

## 解决方案
- `scripts/refresh_status.py`：复用 `compute_status()` 按当前北京时间重算 `status`、`status_basis`、`sort_key`，并更新 `status_as_of`；结构幂等，支持 `--dry`。
- `.github/workflows/healthcheck.yml`：每日 `schedule` 触发探活，并执行一次 `--dry` 重算演练（只报告不写回，避免 CI 自动提交）。
- 需要真正刷新产出时，由维护者执行 `python scripts/refresh_status.py` 后随 PR 提交。

## 边界
`status` 仍不是实时计算值，界面层不得声称「实时更新」；查询时刻以 `status_as_of` 为准。
