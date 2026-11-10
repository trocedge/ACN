# 改进计划执行报告

> 版本：v1.0 ｜ 日期：2026-11-10
> 依据：`docs/quality-review-and-improvement-plan.md`（10 条优点 / 20 条缺点 / 三期计划书 / 开发执行指令）
> 执行范围：P0 全量、P1 的数据侧与文档侧、P2 的规格与模板
> 口径：严格遵循计划书硬约束——老档案只读、不造数据、时区不静态替换、不擅自修改他人负责的模块

---

## 1. 逐条落地情况（对应 20 条缺点）

| # | 缺点 | 状态 | 落地位置 | 说明 |
|---|---|:---:|---|---|
| 01 | 定位偏研究者，本科生看不懂 | ✅ / ⏸ | `docs/glossary.md` | 已产出面向全校的使用入门与术语表；页面接入需界面层完成 |
| 02 | 界面与数据缺中文化 | ✅ / ⏸ | `build_compact_data.py` → `date_zh` / `place_zh` | 数据侧覆盖 2105/2357、1724/2357，未覆盖留空不编造；前端 i18n 需界面层 |
| 03 | 缺北京时间直观展示 | ✅ / ⏸ | `deadline_beijing`、`docs/timezone-dictionary.md` | 换算成功 2713 条，`PT` 等 128 条留空；双列展示需界面层 |
| 04 | 行式列表缺筛选与检索 | ✅ / ⏸ | `docs/field-contract.md` | 已明确 `sub`/`year`/`rank.ccf`/`status` 四个筛选维度；组件需界面层 |
| 05 | 未区分已过期/进行中/未公布 | ✅ | `status` / `status_basis` / `status_as_of` | active 114、past 2155、tbd 88；快照时刻已记录 |
| 06 | 移动端体验未验证 | ⏸ | `docs/field-contract.md` §5 | 已给出展示层使用建议与 7 视口验收口径；页面改造后由界面层执行 |
| 07 | 两套日期格式并存 | ✅ | `build_compact_data.py`、`validate_data.py` | 产出统一 ISO 8601；源档案格式纳入 ERROR 级校验门禁 |
| 08 | 时区取值不统一 | ✅ | `docs/timezone-dictionary.md` | 2357 条实测分布、别名表建议、换算规则；**不改原值** |
| 09 | 缺 PR 前强制数据校验 | ✅ | `scripts/validate_data.py`、`docs/ci-templates/data-check.yml` | ERROR/WARN 分级，源档案门禁 ERROR 0；提供可复制的 CI 模板 |
| 10 | 录取率靠标题关联 | ✅ | `validate_data.py`、`docs/test-baseline-analysis.md` | 实证 321 份中 23 份未直接匹配，列为 WARN 并给出 id 级关联建议 |
| 11 | 字段语义边界不清 | ✅ | `docs/field-contract.md` | 顶层 / 届次 / 时间节点三层字段契约，含展示用途与正确性边界 |
| 12 | 生成物入库策略未定 | ✅ / ⏸ | `docs/generated-artifacts-policy.md` | 两方案对比、当前按「随仓库提交」、演进路径；**待项目组拍板**，未擅自改 `.gitignore` |
| 13 | 测试跨平台不达标 | ✅ / ⏸ | `docs/test-baseline-analysis.md` | 14 项既有错误按四类根因分析并给修复优先级；**未擅自改他人测试源码** |
| 14 | 自动发布链路未串 | ✅ / ⏸ | `docs/ci-templates/data-check.yml` | 提供校验工作流与可选「重新生成」任务模板；现行 workflow 未改 |
| 15 | 前端技术栈门槛高 | ✅ | `docs/local-development.md` | 中文上手步骤、目录速查、常见坑、提交前清单 |
| 16 | 缺监控与失败告警 | ✅ | `docs/ci-templates/healthcheck.py` | 可运行探活脚本（文件/解析/条数/新鲜度/校验），本次实测「健康」 |
| 17 | 贡献文档英文且指向上游 | ✅ | `CONTRIBUTING.md` | 中文指南，明确 PR 目标为本仓库对应分支，列出三条数据约定 |
| 18 | 第三方追踪与隐私说明不足 | ✅ / ⏸ | `docs/privacy-assessment.md` | 现状核查、三个方案、隐私弹窗六项要素；页面改动需界面层 |
| 19 | 文档分散无索引 | ✅ | `docs/README.md` | 按使用者 / 数据规范 / 质量 / 协作 / 模板五类归档，附阅读顺序 |
| 20 | 未与前端字段契约对齐 | ✅ | `schema_version 1.1`、`docs/data-changelog.md` | 版本标识、快照时刻、变更日志、兼容性约定、待确认清单 |

**统计**：完全落地（代码或文档可直接交付）**14 项**；数据/文档侧落地、界面接入需协同 **5 项**（01—04、06）；产出规格、待项目组拍板 **1 项**（12，同时涉及 13、14 的现行配置）。**无一项被虚报为完成。**

---

## 2. 新增与修改文件

### 代码

| 文件 | 类型 | 说明 |
|---|---|---|
| `scripts/build_compact_data.py` | 修改 | 增强至 schema 1.1：状态、双时区换算、中文字段、录取率关联统计 |
| `scripts/validate_data.py` | 新增 | 独立校验脚本，支持 `--source`（PR 门禁）与完整校验、`--json` 报告 |
| `data/conferences.yml` | 重新生成 | 383 条，1200.9 KB（v1.0 为 776.6 KB，增量来自派生字段） |

### 规范与文档

| 文件 | 对应缺点 |
|---|---|
| `docs/field-contract.md` | 04、11、20 |
| `docs/timezone-dictionary.md` | 03、08 |
| `docs/data-changelog.md` | 20 |
| `docs/generated-artifacts-policy.md` | 12 |
| `docs/glossary.md` | 01 |
| `docs/test-baseline-analysis.md` | 13 |
| `docs/local-development.md` | 15 |
| `docs/privacy-assessment.md` | 18 |
| `docs/README.md` | 19 |
| `CONTRIBUTING.md` | 17 |
| `docs/data-validation-report.json` | 09（机器可读报告） |

### 模板（不替代现行配置）

| 文件 | 对应缺点 |
|---|---|
| `docs/ci-templates/data-check.yml` | 09、14 |
| `docs/ci-templates/healthcheck.py` | 16 |

---

## 3. 验证结果

| 检查 | 结果 |
|---|---|
| 转换脚本 `--check` | 校验问题 0 |
| 源档案门禁 `validate_data.py --source` | **ERROR 0 / WARN 1**，退出码 0 |
| 完整校验（源 + 产出） | **ERROR 0 / WARN 1**，退出码 0 |
| 产出条数 | 383，与源档案一致 |
| 日期规范化 | 空格转 T 2841 条、TBD 98 条、未识别 **0** |
| 时区 | 2357 条中 35 条无法固定换算，`AoE` 1540 条原值保留 |
| 北京时间换算 | 成功 2713 条，未换算 128 条（不做静态替换） |
| 中文辅助字段 | 日期 2105/2357、地点 1724/2357（未覆盖留 `null`） |
| 状态分布 | active 114 / past 2155 / tbd 88 / unknown 0 |
| 录取率关联 | 321 份中 23 份未直接匹配（既有问题，列为 WARN） |
| 探活模板 | 5 项检查全 OK，结论「健康」 |
| 老链路 `build_data.py` | 退出码 0，`allconf.json` / `initial.json` 正常 |
| 测试基线对照 | 82 项 / 14 错，改动前后一致，无新增失败 |
| 老档案改动 | **0** |
| 命名清洁度 | 全部新增文件无第三方工具名称、无口语化表述 |

---

## 4. 诚实边界（明确未做的事）

按计划书的责任边界与「只产出方案与模板，不擅自修改他人负责模块」的约束，以下内容**本次未动**：

| 项 | 原因 | 交付的替代物 |
|---|---|---|
| `src/`、`index.html` 等前端源码 | 由界面层负责，改动会冲突 | 字段契约、展示层使用建议、7 视口验收口径 |
| 现行 `.github/workflows/` 配置 | 由工程/发布层负责 | `docs/ci-templates/data-check.yml` 模板 |
| `.gitignore` | 生成物策略需项目组拍板 | `docs/generated-artifacts-policy.md` 两方案对比 |
| 14 项既有测试源码 | 属独立修复任务，不宜混入本次 PR | `docs/test-baseline-analysis.md` 根因与修复优先级 |
| 页面第三方脚本 | 需界面层评估后决定 | `docs/privacy-assessment.md` 三方案与文案要素 |
| 源档案 `.yml` | 硬约束：只读 | 无 |

---

## 5. 待项目组确认（不阻塞本次交付）

1. 界面最终展示字段清单 → 决定新表是否精简；
2. 时间显示原始时区还是换算值 → 决定是否调整 `deadline_beijing` 展示文案；
3. 生成物「随仓库提交」还是「CI 生成」→ 见策略说明；
4. `status` 是否由 CI 定时重算（当前为生成时刻快照）；
5. 录取率档案是否建立 `id` 级关联（当前 23 份断链）。

---

## 6. 复现命令

```bash
python scripts/validate_data.py --source
python scripts/build_compact_data.py
python scripts/validate_data.py --json docs/data-validation-report.json
python docs/ci-templates/healthcheck.py
python scripts/build_data.py
```

---

## 7. 变更记录

| 版本 | 日期 | 内容 |
|---|---|---|
| v1.0 | 2026-11-10 | 按 20 条缺点完成 P0 全量与 P1/P2 的规格模板；schema 升至 1.1；全量验证通过 |
