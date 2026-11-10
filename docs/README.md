# 文档索引

> 最后更新：2026-11-10
> 本页是 `docs/` 的统一入口，按用途分类。贡献规范见仓库根目录 `CONTRIBUTING.md`。

---

## 面向使用者

| 文档 | 内容 |
|---|---|
| `glossary.md` | 站点使用入门、术语表、时区注意事项、筛选建议 |

## 数据规范（本次改造核心）

| 文档 | 内容 |
|---|---|
| `data-format-specification.md` | 数据格式规范、字段映射、时区处理、验证结果 |
| `field-contract.md` | 前后端唯一字段依据：语义、必填性、展示用途、派生边界 |
| `timezone-dictionary.md` | 2357 条时区实测分布、换算规则、处理约定 |
| `data-changelog.md` | schema 版本演进（v1.0 → v1.1）与兼容性约定 |
| `generated-artifacts-policy.md` | 生成物「随仓库提交 / CI 生成」两方案对比与待决项 |
| `data-validation-report.json` | 最近一次校验的机器可读报告 |

## 质量与改进

| 文档 | 内容 |
|---|---|
| `quality-review-and-improvement-plan.md` | 10 条优点、20 条缺点、三期改进计划书、开发执行指令（提示词） |
| `optimization-plan-40.md` | 针对 40 条差距的逐条详细方案、验收与增量提示词（含总指令） |
| `implementation-report.md` | 20 条缺点逐条落地状态、验证数字、诚实边界、待确认 5 项 |
| `gap-to-full-score.md` | 四维度各 10 条（共 40 条）「距离满分差在哪」与补齐动作 |
| `test-baseline-analysis.md` | 既有测试错误的根因分类与修复建议 |
| `test-fix-plan.md` | 测试修复进展（14→12 错）与剩余 12 项补丁 |
| `acceptance-40.md` | 40 条逐条验收表与状态汇总 |
| `full-audit-score.md` | **全方位实测评分报告**：13 项实测、五维重评、双口径总分、扣分明细、天花板与最短路径 |
| `full-score-push-report.md` | **最新评分**：补分执行、A 账 98.6 / B 账 57、剩余硬边界与最短路径 |
| `zh-preview.html` | 中文辅助层接入参考实现（术语 / 筛选 / 双时区 / 纠错 / 隐私，可运行） |
| `responsive-report.md` / `perf-report.md` | 7 视口实测与性能基准（本机 Edge headless） |
| `ci-red-green-report.md` / `status-refresh.md` | CI 红绿验证记录与状态重算说明 |
| `doc-stats-check.md` | 历史硬编码数字自动核查清单 |
| `deduction-ledger.md` | **逐分扣分台账**：A 账 22 单元（扣 4.2）、B 账 13 单元（扣 59）、11 条外部动作映射、两处口径修正、回分表 |
| `corrections.md` | **重要**：此前不准确表述的更正记录，对外汇报以此为准 |
| `unparsed-fields.md` | 中文辅助字段未覆盖清单（自动生成的原始数据） |
| `timeline-order-observations.md` | 校验 WARN 的 3 处观察项明细 |
| `rollback-drill.md` | 回退演练记录 |

## 开发与协作

| 文档 | 内容 |
|---|---|
| `../CONTRIBUTING.md` | 中文贡献指南：改哪个文件、必填字段、分支与 PR 规范 |
| `local-development.md` | 本地启动步骤、目录速查、常见坑 |
| `privacy-assessment.md` | 第三方资源现状与隐私告知建议 |
| `../scripts/DATA_LOADING.md` | 原有数据加载与构建流程（仓库既有） |

## 模板（供工程化接入，非现行配置）

| 文件 | 内容 |
|---|---|
| `ci-templates/data-check.yml` | GitHub Actions 数据校验工作流模板 |
| `ci-templates/healthcheck.py` | 数据新鲜度与链接可用性探活脚本模板 |
| `pr-description.md` / `pr-summary.md` | 可粘贴的 PR 描述与评审一页纸 |
| `decisions.md` / `field-contract-signoff.md` / `collaboration-raci.md` | 待勾选的决策表、字段确认表、任务分派表 |
| `candidate-README.zh-CN.md` / `readme-zh-entry.md` | 中文第一入口候选与可粘贴片段 |
| `upstream-sync.md` / `rollback-drill.md` | 上游同步约定与回退演练 |
| `ui-spec-*.md` | 10 份界面接入规格（术语、中文、双时区、筛选、默认视图、响应式、分页、页脚、纠错、隐私） |

---

## 阅读顺序建议

| 你是… | 建议顺序 |
|---|---|
| 第一次来的同学 | `glossary.md` → `quality-review-and-improvement-plan.md` |
| 负责界面改造 | `field-contract.md` → `timezone-dictionary.md` → `generated-artifacts-policy.md` |
| 负责数据维护 | `../CONTRIBUTING.md` → `local-development.md` → `data-format-specification.md` |
| 负责工程与发布 | `ci-templates/` → `test-baseline-analysis.md` → `generated-artifacts-policy.md` |
| 评审本次 PR | `data-format-specification.md` → `data-changelog.md` → `data-validation-report.json` |

---

## 维护约定

1. 新增文档必须同步更新本索引；
2. 字段结构变更必须同步 `field-contract.md` 与 `data-changelog.md`，并递增 `schema_version`；
3. 文档中的统计数字应注明统计口径与日期，避免过期数值被当作实时值；
4. 模板类文件只提供方案，不直接替代现行配置。
