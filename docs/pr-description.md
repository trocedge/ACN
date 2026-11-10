# PR 描述（可直接粘贴，2026-11-10 21:35 更新）

## 改动范围

新增数据格式转换、校验体系、中文辅助层与工程模板，覆盖 `scripts/`、`data/`、`docs/`、`.github/workflows/`。
**不修改、不删除任何 `conference/**/*.yml` 源档案；既有 4 个 workflow 未改动。**

- `scripts/build_compact_data.py`：383 份散档合并为 schema 1.1 单表；状态、双时区换算（PT 夏令时独立推算字段）、中文辅助字段、TBD 跟踪、排序键。
- `scripts/validate_data.py`：ERROR/WARN 分级校验，支持 `--source` 门禁与 JSON 报告。
- 新增 `scripts/pipeline.py`（一键全链路）、`refresh_status.py`、`deadline_compat.py`、`ci_red_green_check.py`、`check_doc_stats.py`。
- `data/`：`conferences.yml`（383 条）、`conferences.json`（浏览器可读）、`glossary.json`、`i18n/zh.json`、`filter-index.json`、`feedback-schema.json`。
- `docs/zh-preview.html`：中文辅助层接入参考实现（术语引导、四维筛选、双时区并列、纠错入口、隐私清单、分页）。
- 新增 workflow：`data-check.yml`（PR 数据门禁）、`healthcheck.yml`（每日探活与状态重算演练）。

## 验证结果（本机实测）

| 项 | 结果 |
|---|---|
| 全量单测 | **100 项 OK（skipped=1）**，错误 12 → 0；10 项由 Edge headless 真跑通过，1 项 symlink 因 Windows 权限 `skipTest` 并写明原因，**未删任何断言** |
| 源档案门禁 / 完整校验 | ERROR **0** / WARN 1（3 处 timeline 顺序观察项，源档案只读）；产出 383 条一致 |
| 老数据链路 | `build_data.py` 退出码 0 |
| CI 红绿验证 | 改坏 deadline → 门禁 exit 1 阻断 → 字节级恢复 + sha256 复核 → 绿灯 exit 0 |
| 全链路流水线 | `pipeline.py` 六步 **6/6 通过** |
| 响应式与性能 | 7 视口 **7/7** 无溢出 / 字号 / 热区全过，载入均值 37.39 ms |
| 中文覆盖 | 日期 2277/2357、地点 2251/2357（未覆盖 106 条留空，不编造译名） |
| 边界 | 老档案、`src/`、`index.html`、既有 4 个 workflow **零改动** |

## 诚实边界

- 前端 `src/`、`index.html` 未改（界面层负责）；`zh-preview.html` 是**接入参考实现 / 验证页**，不是主站界面。
- 新增 workflow 需推送合并后生效；探活通知通道仍为接口约定，未接实际告警。
- `status` 是生成时刻快照，非实时值；`AoE` 1540 条原值保留，`PT` 128 条按日期推算，均不做静态替换。
- 12 项历史测试错误已修复，根因与 Windows 环境差异见 `docs/test-fix-plan.md`。
- 性能基准在 headless 虚拟时间下计时精度受限，筛选 0 ms 表示未观测到可测量开销，**不等同真实设备性能**。
- 内部自评结论见 `docs/full-score-push-report.md`；不代表官方评分。

## 待确认 5 项

字段清单 / 时间展示口径 / 生成物策略 / `status` 重算方式 / 录取率 id 关联（勾选表见 `docs/decisions.md`）。
