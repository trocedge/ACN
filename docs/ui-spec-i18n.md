> 交付规格：数据侧已就绪，界面层按本文件接入；本分支不改前端源码。

# 中文界面键表接入规格（第 12 条）
数据源：`data/i18n/zh.json`。
| 键组 | 用途 |
|---|---|
| status | active/past/tbd/unknown 四值文案 |
| status_basis | beijing/pt_dst/local_naive/none 四值说明 |
| timezone_hint | AoE 提示、null 时的「需按日期换算」、TBD 提示 |
| filters | 四个筛选维度标签 |
| footer | 免责与 `status_as_of` 标注 |
**回退规则**：`date_zh` / `place_zh` 为 `null` 时显示英文原值，绝不显示空字符串。
验收：切换后枚举无遗漏；7 视口不溢出（由界面层回归）。
