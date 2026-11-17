> 交付规格：数据侧已就绪，界面层按本文件接入；本分支不改前端源码。

# 双时区并列展示规格（第 13 条）
| 分支 | 左列 | 右列 |
|---|---|---|
| 有 `deadline_beijing` | `deadline` + `timezone` | `deadline_beijing`（标「北京时间」） |
| 仅 `deadline_beijing_dst` | 同上 | 推算值 + 「按夏令时推算」标注 |
| `tbd` / 均为 null | 同上 | 「需按日期换算」或「尚未公布」 |
`AoE` 条目加提示气泡：UTC-12，比北京时间晚 20 小时，跨日必须保留。
验收：三种分支齐全；`docs/timezone-checklist.md` 抽样 10 条人工核对。
