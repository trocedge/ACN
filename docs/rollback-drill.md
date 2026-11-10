# 回退演练记录（第 30 条）
> 在临时 worktree 中基于 `main`（不含本次任何新增文件）验证「删新增文件即可回退」。
| 项 | 结果 |
|---|---|
| 演练方式 | `git worktree add --detach /d/Temp/acn-rollback main`，不动主工作区 |
| 老链路 | `python scripts/build_data.py` 退出码 0 |
| 产物 | `public/conference/allconf.json` 正常生成 |
| 依赖 | 仅需 PyYAML（仓库既有） |
| 清理 | `git worktree remove --force`，主工作区未受影响 |
| 结论 | 设计假设成立：本次改动全部为新增文件，移除后老链路可独立运行 |
