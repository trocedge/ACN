# 字段契约确认表（第 36 条）
> 界面负责人逐字段勾选；未确认项标注「影响界面接入」，不代为勾选。
| 层级 | 字段 | 是否展示 | 展示位置 | 备选 | 确认 |
|---|---|---|---|---|---|
| 顶层 | title / description | 是 | 行标题 / 副标题 | — | ☐ |
| 顶层 | sub / rank.ccf | 是 | 筛选与徽标 | — | ☐ |
| 顶层 | status_as_of | 是 | 页脚 | — | ☐ |
| 顶层 | source_file / schema_version | 否 | 排错与兼容 | — | ☐ |
| 届次 | deadline + timezone | 是 | 双时区左列 | — | ☐ |
| 届次 | deadline_beijing / _dst | 是 | 双时区右列 | — | ☐ |
| 届次 | date_zh / place_zh | 是 | 详情 | 回退英文 | ☐ |
| 届次 | status / status_basis | 是 | 默认过滤与说明 | — | ☐ |
| 届次 | sort_key | 否 | 排序 | — | ☐ |
| 节点 | tbd_* 跟踪字段 | 否 | 维护用 | — | ☐ |
