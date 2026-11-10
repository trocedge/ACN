> 交付规格：数据侧已就绪，界面层按本文件接入；本分支不改前端源码。

# 筛选与搜索规格（第 14 条）

数据源：`data/filter-index.json`（四维枚举由产出直接生成）。

| 维度 | 字段 | 值域 |
|---|---|---|
| 学科 | `sub` | 10 类 |
| 年份 | `events[].year` | 10 个年份 |
| CCF 等级 | `rank.ccf` | A/B/C/N |
| 状态 | `events[].status` | active/past/tbd |

搜索字段：`title`、`description`；383 条过滤目标 <100ms。
