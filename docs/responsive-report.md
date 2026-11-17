# 响应式与性能实测报告

> 由 `docs/ci-templates/viewport-check.py` 驱动本机 Edge headless 实测，非纸面规格。
> 页面：`docs/zh-preview.html`（中文辅助层接入参考实现），数据来源 `data/conferences.json`。

| 视口 | 无横向溢出 | 正文字号 >=12px | 点击热区 >=44px | 渲染行数 | 筛选耗时 |
|---:|---|---|---|---:|---:|
| 320 px | 是 | 是 (14 px) | 是 (44 px) | 50 | 0 ms |
| 375 px | 是 | 是 (14 px) | 是 (44 px) | 50 | 0 ms |
| 414 px | 是 | 是 (14 px) | 是 (44 px) | 50 | 0 ms |
| 768 px | 是 | 是 (14 px) | 是 (44 px) | 50 | 0 ms |
| 1024 px | 是 | 是 (14 px) | 是 (44 px) | 50 | 0 ms |
| 1440 px | 是 | 是 (14 px) | 是 (44 px) | 50 | 0 ms |
| 1920 px | 是 | 是 (14 px) | 是 (44 px) | 50 | 0 ms |

合计：**7 / 7 视口全部通过**。
