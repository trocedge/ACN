# ACN 数据格式变更日志

> 数字与结论更正见 `docs/corrections.md`；对外汇报以更正记录为准。


> 记录 `data/conferences.yml` 结构变化，供展示层判断兼容性与迁移。
> 字段契约：`docs/field-contract.md` ｜ 时区规范：`docs/timezone-dictionary.md`

---

## v1.1（2026-11-10）

### 新增字段

| 字段 | 层级 | 说明 |
|---|---|---|
| `schema_version` | 顶层 | 结构版本标识，当前 `1.1` |
| `status_as_of` | 顶层 | 状态字段生成时刻（北京时间），说明 `status` 是快照 |
| `source_file` | 顶层 | 源档案相对路径，便于回溯 |
| `timezone_utc_offset` | 届次 | 可确定的 UTC 偏移；`PT` 等为 `null` |
| `deadline_beijing` | 时间节点 | 按可确定偏移换算的北京时间；不可换算为 `null` |
| `date_zh` | 届次 | 中文日期，仅按结构化规则转换，无法确定为 `null` |
| `place_zh` | 届次 | 中文地点，城市名保留原文，无法确定为 `null` |
| `status` | 届次 | `active` / `past` / `tbd` / `unknown`，用于默认过滤 |
| `status_basis` | 届次 | `beijing` / `local_naive` / `none`，标注判定依据 |

### 变更

| 项 | v1.0 | v1.1 |
|---|---|---|
| 脚本文件 | `scripts/build_compact.py` | `scripts/build_compact_data.py` |
| `confs` | → `events` | 保持不变 |
| `deadline` | ISO 8601 | 保持不变，新增并列换算值 |
| 文档 | 单一交付说明 | 拆分为规范、字段契约、时区字典、变更日志 |

### 不变（重要）

- 老 `conference/**/*.yml` 一个字未改，贡献方式不变。
- `rank` / `dblp` / `date` / `place` 英文原值全部保留。
- `AoE` 1540 条原值保留，未做静态时区替换。
- 原有 `build_data.py` → `allconf.json` 链路保持可用。

### 验证

| 项 | 结果 |
|---|---|
| 源档案门禁（`validate_data.py --source`） | ERROR 0 / WARN 1 |
| 完整校验（源 + 产出） | ERROR 0 / WARN 1 |
| 产出条数 | 383，与源档案一致 |
| 北京时间换算 | 成功 2713 条 / 未换算 128 条 |
| 中文字段覆盖 | 日期 2105/2357、地点 1724/2357（未覆盖留空） |
| 状态分布 | active 114 / past 2155 / tbd 88 / unknown 0 |
| 产出体积 | 1200.9 KB（v1.0 为 776.6 KB，增量来自派生字段） |

> WARN 1 项为「录取率档案 23 份未与会议标题直接匹配」，属仓库既有问题，非本次改动引入。

---

## v1.0（2026-11-09）

- 新增 `scripts/build_compact.py` 与 `data/conferences.yml`；
- 383 份散装档案合并为单表，`confs` → `events`，日期统一 ISO 8601；
- 保留时区原值并补 `timezone_utc_offset`；
- 老文件零改动，老链路 `build_data.py` 验证照常执行。

---

## 版本兼容约定

1. 展示层应先读 `schema_version`，不认识的字段一律忽略而不是报错。
2. 新增字段只做加法；删除或改名必须递增主版本并同步本日志与字段契约。
3. `status` 是生成时刻快照，长期方案由 CI 定时重算（见《生成物入库策略说明》）。
