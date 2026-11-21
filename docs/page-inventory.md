# 页面清单（2026-11-22 首页竞赛化改造）

按学长 2026-11-21 反馈整理：理清当前所有页面，明确保留与退出，所有对外内容归属 competition。

## 保留页面

| 页面 | 生成方式 | 定位 |
|---|---|---|
| `/` | Rust/Leptos 前端 | 竞赛资讯首页（本轮改造，唯一主展示界面） |
| `/competition/` | `scripts/generate_competition_pages.py` | 白名单竞赛大全，二级参考名录 |
| `/competition/c01/` … `c84/` | 同上 | 单项竞赛详情页 |

## 退出部署的页面（原会议项目体系）

| 页面 | 原生成方式 | 处理 |
|---|---|---|
| `/venues/` | `generate_seo_pages.py` | 不再生成，源脚本保留在仓库 |
| `/venues/<sub>/` 会议分类页 | 同上 | 同上 |
| 会议系列页 / 年份页 / 分享页 | 同上 | 同上 |
| `?view=table` 等旧展示模式 | 前端残留能力 | 不再作为对外入口 |

「退出部署」= 部署流程不再调用对应生成步骤、新产物不再包含这些页面；**不是删除源文件**，`archive/conference/` 与旧脚本保留在仓库历史中，可随时回退。

## 不动的部分

- 飞书通知（`notify_feishu.py` 等）：其他同学负责，本轮不改。
- `merge_check.yml` 中日历/RSS 生成（PR #4 学长刚修的）：保持原样。
- 会议数据源文件 `archive/conference/`：物理保留。

## 数据填写规范（competition/whitelist.yml）

必填字段：`seq`（官方序号 1—84，勿动）、`title`（官方目录原文名）、`sub`（types.yml 中的短码）、`category`（官方分类原文）。

可选字段——**只在核实官方公告后填写**：

```yaml
- seq: 1
  title: '中国国际 "互联网+"大学生创新创业大赛'
  sub: COMP
  category: 综合类
  site: https://cy.ncss.cn/          # 官网，核实过才填
  deadline: '2027-03-15T18:00:00'    # ISO 8601，北京时间
  timezone: Asia/Shanghai
  source_url: '截止时间的官方公告地址'   # 有 deadline 必填
```

校验规则（`scripts/validate_competition.py`，CI 强制）：

1. seq 整数、全局唯一，正式名单 1—84 连续
2. title 非空且不重复
3. sub 必须存在于 types.yml
4. site 省略或合法 http/https 链接
5. deadline 省略或合法 ISO 8601，禁止"大概月底"类模糊文本
6. 有 deadline 必须有 source_url；timezone 仅支持 Asia/Shanghai
7. 构建产物 whitelist.json 与源 YAML 条数、序号一致

本地验证命令：

```bash
python scripts/validate_competition.py      # 校验
python scripts/build_data.py                # 构建
python scripts/test_validate_competition.py # 校验器单测
```

新增一条带日期数据的最小流程：改 `competition/whitelist.yml` → 跑上面三条命令 → 本地打开首页确认卡片显示 → 提交。
