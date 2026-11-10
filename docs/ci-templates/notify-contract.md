# 探活与通知接口约定（第 25 条）
| 项 | 约定 |
|---|---|
| 触发 | CI `schedule`（建议每日一次）+ `workflow_dispatch` 手动 |
| 检查 | `python docs/ci-templates/healthcheck.py --json <报告路径>` |
| 归档 | 按运行编号命名，不做覆盖 |
| 失败 | 退出码非 0；通知通道由通知脚本负责人提供占位接口 |
| 禁止 | 不在模板中写死账号、密钥或外部地址 |
