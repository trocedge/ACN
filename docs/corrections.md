# 更正记录（重要，请勿引用旧数字）
> 本轮复核发现并修正了此前文档中的若干不准确表述，统一在此登记。
| # | 此前表述 | 更正后 | 依据 |
|---|---|---|---|
| 1 | 「录取率档案 23 份断链」 | **误报，实为 0 份** | 仓库以文件名 stem 关联：`accept_rates/AI/nips.yml` 对应 `conference/AI/nips.yml`（title 为 NeurIPS）。此前按标题比对判据过粗，已修正 `validate_data.py` 与 `build_compact_data.py`，23 份映射见 `docs/accept-rate-mapping.yml` |
| 2 | 「缺 PR 前强制数据校验」 | **不准确** | 仓库既有 `merge_check.yml` 已运行 `scripts/validate.py`（jsonschema 门禁）与 `build_data.py`；真实差距是「新数据格式未纳入既有门禁」，本次新增 `data-check.yml` 补齐 |
| 3 | 「WARN 1 = 录取率断链」 | **WARN 1 = timeline 顺序观察项 3 处** | 扩展校验规则发现的真实观察项，明细见 `docs/timeline-order-observations.md`，仅提示不阻断 |
| 4 | 中文覆盖 2105/1724、local_naive 35 | **2277/1912、local_naive 0** | 扩充跨月日期解析、国家与地点别名表、PT 夏令时推算后实测；实时数字以 `docs/stats.md` 为准 |
| 5 | 「CI 模板未启用」 | **既有 CI 已启用，本次为新增覆盖** | 见第 2 条；`data-check.yml` 为新增工作流，不改动既有 4 个 |
| 6 | 测试基线 82 项 / 14 错 | **100 项 / 12 错** | 补齐 `icalendar` 使 2 个加载失败消失，并新增 11 项单测；错误数下降 2，未新增失败，详见 `docs/test-fix-plan.md` |
| 7 | 「推送 PR 后产品口径约 61 分（+20）」 | **56 分（+15）** | 逐分台账拆开后发现把「探活调度与通知接入」（P2-4，5 分）误算进推送收益；推送本身只回 P2-1/P2-2/P2-3 共 15 分。天花板表与性价比表已同步更正，逐分依据见 `docs/deduction-ledger.md` §4.1 |
> 历史文档保留原有叙述以便追溯，但**对外汇报与 PR 描述请以本表为准**。
