# 40 条逐条验收表（按计划书执行结果）

> 日期 2026-11-10。状态分三类：**已实现并验证**（代码/数据/配置跑通）、**成品已就绪**（文档/模板可直接交付）、
> **需一次外部动作**（账号授权、项目组勾选或界面层接入）。不把「需外部动作」虚报为完成。

| # | 条目 | 状态 | 证据 |
|---|---|---|---|
| 01 | 时区别名归一化 | 已实现并验证 | docs/timezone-alias.json + 脚本读取；报告输出「时区 6 项」 |
| 02 | PT 夏令时换算 | 已实现并验证 | pacific_offset() + deadline_beijing_dst；128 节点有值，local_naive 归 0 |
| 03 | TBD 跟踪 | 已实现并验证 | 98 条含 tbd_review/source/owner；tbd_reminder.py 可输出清单 |
| 04 | 中文日期覆盖 | 已实现并验证 | 2105→2277/2357；跨月区间解析；未覆盖清单 docs/unparsed-fields.md |
| 05 | 中文地点覆盖 | 已实现并验证 | 1724→1912/2357；place-aliases.yml 19 项；未覆盖清单可核查 |
| 06 | 录取率关联 | 误报已修正 | 判据改按文件名 stem，321 份 0 未匹配；23 份映射表可核查 |
| 07 | status 实时化 | 数据侧已实现 / CI 待拍板 | status_basis 新增 pt_dst 35 条；定时重算给 artifact-strategy-b.yml |
| 08 | 校验规则扩充 | 已实现并验证 | 5 类 WARN 规则 + 6 项单测；真发现 3 处 timeline 顺序观察项 |
| 09 | 日期格式收敛 | 方案已定稿 | docs/date-format-migration.md 推荐双轨，含收敛条件 |
| 10 | 版本迁移与兼容 | 已实现并验证 | migrate_schema.py 幂等 dry-run；test_schema_compat 5 项通过 |
| 11 | 术语引导数据 | 成品已就绪 | data/glossary.json + ui-spec-glossary.md；页面接入需界面层 |
| 12 | 中文键表 | 成品已就绪 | data/i18n/zh.json 覆盖全部枚举 + 回退规则 |
| 13 | 双时区规格 | 成品已就绪 | ui-spec-dual-timezone.md 三分支 + timezone-checklist.md 10 条抽样 |
| 14 | 筛选索引 | 已实现并验证 | data/filter-index.json 由产出生成：10 学科/10 年份/4 等级/3 状态 |
| 15 | 默认过滤规格 | 成品已就绪 | ui-spec-default-view.md；status 字段已在数据侧 |
| 16 | 移动端回归 | 规格已就绪 / 执行需界面层 | 7 视口与 6 检查项 + check-responsive.py；页面改造后执行 |
| 17 | 排序与分页 | 已实现并验证 | sort_key 写入 383 条；ui-spec-pagination.md |
| 18 | 页脚免责 | 成品已就绪 | ui-spec-footer.md 可直接粘贴，含 status_as_of 映射 |
| 19 | 纠错入口 | 成品已就绪 | data/feedback-schema.json + ui-spec-feedback.md，指向本仓库 Issues |
| 20 | 隐私文案 | 成品已就绪 / 页面改动需界面层 | ui-spec-privacy.md 六项要素，未核实项保留占位 |
| 21 | CI 门禁 | 已落地 / 推送后生效 | 新增 .github/workflows/data-check.yml，未改既有 4 个；红绿步骤在 ci-enablement.md |
| 22 | 本地钩子 | 成品已就绪 | pre-commit + hooks-setup.md，局部配置不改全局 |
| 23 | 14 项测试错误 | 部分修复并验证 | icalendar 补齐，错误 14→12；新增 11 项单测全过；余 12 项补丁在 test-fix-plan.md |
| 24 | 测试依赖 | 成品已就绪 | requirements-test.txt + clean-env-check.md |
| 25 | 探活调度与通知 | 模板已就绪 / 接入需工程层 | healthcheck.py 实测健康；notify-contract.md 含失败分支，无凭据 |
| 26 | 生成物策略 | 两方案已就绪 / 待拍板 | artifact-strategy-a/b.yml + decisions.md 勾选栏 |
| 27 | 完整流水线 | 成品已就绪 | full-pipeline.yml 五步骨架，标注依赖第 26 条 |
| 28 | 校验趋势 | 已实现并验证 | report_trend.py + validation-trend.md；无历史报告时如实标「无数据」 |
| 29 | 体积门禁 | 已实现并验证 | size-gate.yml + size-baseline.md；当前 1331.8 KB < 1.5 MB |
| 30 | 回退演练 | 已真实执行 | 临时 worktree 基于 main 跑老链路 exit 0，产物 777K；rollback-drill.md |
| 31 | PR 描述 | 成品已就绪 / 推送需账号授权 | pr-description.md 四段齐全；GitHub 浏览器授权只能本人完成 |
| 32 | 5 项决策表 | 成品已就绪 / 待项目组勾选 | decisions.md 每项含选项、影响、推荐、复查日 |
| 33 | 中文入口片段 | 成品已就绪 | readme-zh-entry.md 可粘贴，不改英文 README 正文 |
| 34 | 中文 README 候选 | 成品已就绪 / 启用待决定 | candidate-README.zh-CN.md 六段，链接均可达 |
| 35 | 上游同步 SOP | 成品已就绪 | upstream-sync.md 五要素，与 CONTRIBUTING 一致 |
| 36 | 字段契约确认表 | 成品已就绪 / 待界面负责人勾选 | field-contract-signoff.md 逐字段含确认栏，未代为勾选 |
| 37 | 协同任务分派 | 成品已就绪 / 待分派 | collaboration-raci.md 五项含角色与节点，不编造人名 |
| 38 | PR/Issue 模板 | 成品已就绪 | 两个模板含改动范围/验证/风险/待确认等要素 |
| 39 | 统计自动同步 | 已实现并验证 | sync_doc_stats.py 生成 docs/stats.md，数字取自产出与报告 |
| 40 | 评审一页纸 | 成品已就绪 | pr-summary.md 五段，明确写出既有测试错误与本次无关 |

## 汇总

- 共 **40 条**，全部有可交付产物与证据。
- 含「已实现并验证」：12 条；「成品已就绪」：19 条；「部分修复」/「误报已修正」等：9 条。
- **必须外部动作**：推送授权（31）、项目组勾选（26/32/36/37）、界面层接入（11—20）、CI 调度接入（25）、剩余测试补丁单独 PR（23）。
- 更正记录见 `docs/corrections.md`；实时数字见 `docs/stats.md`。

---

## 状态更新（2026-11-10 15:05 补分后）

- 第 23 条（测试错误）：由「部分修复」升级为 **12 错 → 0**，全量 100 项 OK，1 项因 Windows 权限合理跳过；详见 `docs/test-fix-plan.md`。
- 第 16 条（移动端回归）：**7 视口已真实执行 7/7 通过**，报告 `docs/responsive-report.md`；但主站 WASM 页面仍需界面层单独回归。
- 第 21 条（CI 门禁）：**红绿验证已本地真实执行**（`docs/ci-red-green-report.md`），推送后生效的状态不变。
- 第 25 条（探活调度）：调度 workflow 已落地（`.github/workflows/healthcheck.yml`），通知通道仍为接口约定。
- 第 11—20 条（界面接入）：数据侧规格已由 `docs/zh-preview.html` 参考实现全部消费，**主站接入状态不变**，仍需界面负责人。
- 第 31 条（推送 PR）：第三次重试仍超时（非交互环境无法完成浏览器授权），**状态不变**。
- 第 07 / 26 / 32 / 34 / 36 / 37 条：决策与确认类，状态不变。